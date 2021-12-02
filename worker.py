from typing import Optional
from celery import Celery

import os

import shitfaced


def setup_celery():
    celery = Celery(__name__)
    celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
    celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
    return celery


celery = setup_celery()


@celery.task(name="process_image")
def create_task(infile, content_type, drawRectangle=Optional[bool]):
    submission = shitfaced.process_image(infile, content_type, drawRectangle=drawRectangle)
    print(submission)
    return submission is not False
