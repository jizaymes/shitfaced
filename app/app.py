from celery.result import AsyncResult

from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from io import BytesIO
from typing import Annotated
from database import ShitfaceDB
import boto3
import hashlib

from mimetypes import guess_extension

from worker import process_image
import config

import util

s3client_incoming = boto3.client("s3", **config.INCOMING_OBJ_STORAGE_CONFIG)
s3client_processed = boto3.client("s3", **config.PROCESSED_OBJ_STORAGE_CONFIG)

tracking_code_url = config.TRACKING_CODE_URL
tracking_code_website_id = config.TRACKING_CODE_WEBSITE_ID

db = ShitfaceDB()
app = FastAPI()

emoji_list = util.get_emoji_list(use_web_path=True)

# Make sure our static files and templates are mapped through for js/css, etc
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("shutdown", db.disconnect_mongo)





def debugLog(msg):
    print(f"{msg}") if config.DEBUG else False


@app.get('/', response_class=HTMLResponse)
async def root_get(request: Request):
    """Return the home page"""
    return templates.TemplateResponse("index.html", {'request': request, 'emoji_list': emoji_list})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    """Return the status of a task"""

    if task_id == 'undefined':
        return False

    debugLog(f"Task ID : {task_id}")
    task_result = AsyncResult(task_id)
    debugLog(f"Task Status : {task_result.status}")
    debugLog(f"Task Result : {task_result.result}")
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": str(task_result.result)
    }
    return JSONResponse(result)


@app.get('/get_shitfaced/{record_id}')
async def get_shitfaced(record_id):
    """Return the actual image file"""
    def iterimage(image):
        with BytesIO(image) as file_like:
            yield from file_like

    shitface_record = db.get_shitface_record(record_id)

    if shitface_record is False:
        return JSONResponse({'error': 'Error: Shitface record is false'})

    bucket = config.PROCESSED_BUCKET
    fn = shitface_record['processed_file_name']

    if not fn:
        return JSONResponse({'error': "Error, no filename"})

    bytes_data = s3client_processed.get_object(Bucket=bucket, Key=fn)

    return StreamingResponse(iterimage(bytes_data['Body'].read()))


@app.post('/upload', status_code=201)
async def upload_file(request: Request, file_upload: Annotated[UploadFile, File(...)], selected_emoji: Annotated[str, Form()]):
    """Process the uploaded file"""

    if not selected_emoji:
        selected_emoji = "poop.png"

    # Check that its valid
    if not file_upload or not util.allowed_file(file_upload.filename):
        return JSONResponse({'error': 'Error, incorrect file'})

    file_contents = await file_upload.read()

    # If its too big, bail out
    if len(file_contents) > config.MAX_ALLOWED_FILESIZE:
        debugLog(f"The file size is {len(file_contents)}")
        debugLog("File too big, bailing out")
        return JSONResponse({'error': 'File too large'})

    # Get a hash of said bytes/file
    file_hash = hashlib.md5(file_contents).hexdigest()

    # Try to see if the image already exists by supplying the file hash
    record_id = db.image_exists(file_hash, selected_emoji)

    # If it does exist, use it
    if record_id is not False:
        debugLog(f"Returned record_id is {record_id}")
        debugLog("Already got a record, going to use that one.")

        return JSONResponse({'record_id': str(record_id)})

    # Create the record
    record_id = db.create_shitface_record(file_hash, file_upload.filename, file_upload.content_type, request.headers)

    # Then load the record
    shitface_record = db.get_shitface_record(record_id)

    # Guess a file extension to append. Chose to do this instead of honor what file extension gets uploaded.
    extension = guess_extension(file_upload.content_type)

    # Give it a new file name
    newfn = str(record_id) + extension

    # create linode file object
    response_obj = s3client_incoming.put_object(Body=file_contents, Bucket=config.INCOMING_BUCKET, Key=newfn)
    
    # Update some info about the file, like the new URL and the log of the file upload
    shitface_record['original_file_url'] = f"{config.INCOMING_BUCKET}/{newfn}"
    shitface_record['original_file_info'] = response_obj
    res = db.update_shitface_record(record_id, shitface_record)

    # If that update failed, yell about it
    if res is False:
        return JSONResponse({'error': "MongoDB Error"})

    task_result = process_image.delay(
        str(record_id),
        file_contents,
        overlay_image=selected_emoji,
        drawRectangle=config.DRAW_RECTANGLE,
    )

    if type(task_result) is dict:
        return JSONResponse(task_result)

    ## TODO: This seems suspect to be removed.
    print(task_result)
    return JSONResponse({'task_id': str(task_result)})
