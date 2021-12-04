# shitfaced
A grouping of microservices using facial recognition to detect and replace faces with the poop emoji.

This uses Python, FastAPI, MongoDB, Celery, Flower, Redis and Docker

The docker image creation takes forever because of dlib and cmake in python. Good luck.

`docker-compose up -d --build`

Then go to web interface at http://localhost:8000 and upload a file, such as one of the included app/test_images/face.jpg files, and it will overlay a poop emoji over the detected faces and return the file to you

This was created after reviewing @testdrivenio's tutorial here [https://testdriven.io/blog/fastapi-and-celery/]