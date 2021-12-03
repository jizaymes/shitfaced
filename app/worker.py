from typing import Optional

from shitfaced import setup_celery, process_image


celery = setup_celery(__name__)


@celery.task(name="process_image")
def create_task(infile, drawRectangle=Optional[bool]):
    submission = process_image(infile, drawRectangle=drawRectangle)
    return submission is not False
