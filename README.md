# shitfaced
Python FastAPI script using face_recognition to detect and replace faces with the poop emoji

run with uvicorn

```
uvicorn app:app --reload
```

Go to web interface at http://localhost:5000 and upload a file, such as one of the included face.jpg files, and it will overlay a poop emoji over the detected faces and return the file to you
