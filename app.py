import shitfaced
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from io import BytesIO

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = FastAPI()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get('/')
async def root_get():
    content = """
    <body>
    <form action="/" enctype="multipart/form-data" method="post">
    <input name="file" type="file">
    <input type="submit">
    </form>
    </body>
    """

    return HTMLResponse(content)


@app.post('/')
async def upload_file(file: UploadFile = File(...)):
    def iterimage(image):
        with BytesIO(image) as file_like:
            yield from file_like

    if file and allowed_file(file.filename):
        # The image file seems valid! Detect faces and return the result.
        content = await file.read()
        image = shitfaced.process_image(content, file.filename)

        return StreamingResponse(iterimage(image.getvalue()), media_type=file.content_type)
    else:
        content = """
        Invalid file format
        """

        return HTMLResponse(content)
