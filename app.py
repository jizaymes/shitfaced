import shitfaced
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from io import BytesIO

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def allowed_file(file):
    return '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get('/', response_class=HTMLResponse)
async def root_get(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})


@app.post('/')
async def upload_file(file: UploadFile = File(...)):
    def iterimage(image):
        with BytesIO(image) as file_like:
            yield from file_like

    if file and allowed_file(file):
        # The image file seems valid! Detect faces and return the result.
        content = await file.read()
        image = shitfaced.process_image(content, shitfaced.DEBUG)

        if image is False:
            content = """
            Invalid file format
            """

            return HTMLResponse(content)

        return StreamingResponse(iterimage(image.getvalue()), media_type=file.content_type)
    else:
        content = """
        Invalid file format
        """

        return HTMLResponse(content)
