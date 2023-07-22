FROM python:3.9.9
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get -y update && apt-get -y install cmake
RUN pip install --upgrade pip && \
    pip install cmake && \
    pip install dlib && \
    pip install face-recognition-models
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
