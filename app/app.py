from rich import inspect
from celery.result import AsyncResult

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from io import BytesIO

import shitfaced
import database

from worker import create_task


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=shitfaced.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("shutdown", database.shutdown_mongo)


@app.get('/', response_class=HTMLResponse)
async def root_get(request: Request):
    """Return the home page"""
    return templates.TemplateResponse("index.html", {'request': request})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    """Return the status of a task"""

    shitfaced.debugLog(f"Task ID : {task_id}")
    task_result = AsyncResult(task_id)
    shitfaced.debugLog(f"Task Status : {task_result.status}")
    shitfaced.debugLog(f"Task Result : {task_result.result}")    
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": str(task_result.result)
    }
    return JSONResponse(result)


@app.get('/get_shitfaced/{mongo_id}')
async def get_shitfaced(mongo_id):
    """Return the actual image file"""
    def iterimage(image):
        with BytesIO(image) as file_like:
            yield from file_like

    bytes_data = await database.get_shitface_image(mongo_id, database.db)
    return StreamingResponse(iterimage(bytes_data))


@app.post('/upload', status_code=201)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Process the uploaded file"""

    if file and shitfaced.allowed_file(file.filename):
        # The image file seems valid! Detect faces and return the result.
        content = await file.read()
        record_id = await database.create_shitface(content, file.filename, file.content_type, request.headers, database.db)

        shitfaced.debugLog(f'Record is : {record_id}')

        task_result = create_task.delay(str(record_id), shitfaced.DEBUG)
        shitfaced.debugLog(f"Image Result is : {task_result}")

        if not task_result:
            return JSONResponse({'error': 'balls'})

        return JSONResponse({'task_id': str(task_result)})
    else:
        return JSONResponse({'error': 'balls, incorrect file'})
