FROM python:3.10
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get -y update && apt-get -y install cmake
RUN pip install --upgrade uv
RUN uv pip install --system cmake && \
    uv pip install --system dlib && \
    uv pip install --system face-recognition-models
COPY ./requirements.txt .
RUN uv pip install --system -r requirements.txt

# copy project
COPY . .