from generate_shitface import generate_shitface
from database import ShitfaceDB
import boto3
import hashlib
import magic
from typing import Optional
import config
from celery import Celery, current_task, states
from mimetypes import guess_extension

s3client_processed = boto3.client("s3", **config.PROCESSED_OBJ_STORAGE_CONFIG)


def setup_celery(name):
    celery = Celery(name)
    celery.conf.broker_url = config.CELERY_BROKER_URL
    celery.conf.result_backend = config.CELERY_RESULT_BACKEND
    return celery


celery = setup_celery(__name__)

db = ShitfaceDB()


def debugLog(msg):
    print(f"{msg}") if config.DEBUG else False


@celery.task(name="process_image")
def process_image(record_id, original_image, overlay_image: Optional[str] = None, drawRectangle: Optional[bool] = False):
    debugLog("About to render the shitface")
    document = db.get_shitface_record(record_id)

    if not document:
        current_task.update_state(state=states.FAILURE, meta={'status': "No Shitface Record in worker:process_image"})
        raise Exception({'error': "Error, No Shitface Record in worker:process_image"})

    shitfaced_file_contents = generate_shitface(original_image, overlay_image=overlay_image, drawRectangle=drawRectangle)
    if type(shitfaced_file_contents) is dict:
        raise Exception(shitfaced_file_contents)

    to_upload = shitfaced_file_contents.getvalue()

    file_hash = hashlib.md5(to_upload).hexdigest()

    existing_record_id = db.image_exists(file_hash, overlay_image)

    if existing_record_id is not False:
        record_id = existing_record_id
        return {'error': 'Already exists, shouldnt get here'}

    else:
        guessed_mimetype = magic.from_buffer(to_upload, mime=True)
        extension = guess_extension(guessed_mimetype)
        newfn = str(record_id) + extension
        response_obj = s3client_processed.put_object(Body=to_upload, Bucket=config.PROCESSED_BUCKET, Key=newfn)

        updates = {
            'overlay_image': overlay_image,
            'processed_file_hash': file_hash,
            'processed_file_info': response_obj,
            'processed_file_url': f"{config.PROCESSED_BUCKET}/{newfn}",
            'processed_file_name': newfn,
            'processed_file_content_type': guessed_mimetype,
        }

        if db.update_shitface_record(record_id, updates):
            return record_id
        else:
            return {'error': 'Could not save the shitfaced file to the DB for some reason'}
