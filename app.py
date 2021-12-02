import shitfaced

from celery.result import AsyncResult

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from io import BytesIO

from worker import create_task


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)
async def root_get(request: Request):
    """Return the home page"""
    return templates.TemplateResponse("index.html", {'request': request})


@app.get('/tasks/{task_id}')
def get_status(task_id):
    """Return the status of a task"""

    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JSONResponse(result)


@app.get('/get_shitfaced/{task_id}')
async def get_shitfaced(task_id):
    """Return the actual image file"""
    def iterimage(image):
        with BytesIO(image) as file_like:
            yield from file_like

    task_result = AsyncResult(task_id)

    return StreamingResponse(iterimage(task_result.result.getvalue()))
#     return StreamingResponse(iterimage(task_result.result.getvalue()), media_type=file.content_type)


@app.post('/upload', status_code=201)
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Process the uploaded file"""

    if file and shitfaced.allowed_file(file.filename):
        # The image file seems valid! Detect faces and return the result.
        content = await file.read()
        image_result = create_task.delay(content, file.content_type, shitfaced.DEBUG)
        image_result = False

        shitfaced.debugLog(image_result)
        if not image_result:
            return JSONResponse({'error': 'balls'})

        return JSONResponse(image_result)
    else:
        return JSONResponse({'error': 'balls, incorrect file'})
