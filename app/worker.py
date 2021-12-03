import os

from celery.exceptions import Ignore
from shitfaced import setup_celery, process_image, debugLog

from pymongo import MongoClient
from bson.objectid import ObjectId

from rich import inspect

celery = setup_celery(__name__)

client = MongoClient(os.environ.get("MONGODB_URL", "mongodb://localhost:27017"))
pymongodb = client.shitfaced


def get_shitface_record_pymongo(record_id, include_images: bool = False):
    debugLog(f'In shitface_pymongo record ID is {record_id}')

    if not pymongodb:
        return False

    filter = {"http_info": 0}

    if not include_images:
        filter = {**filter, "original_file_contents": 0, "shitfaced_file_contents": 0}

    row = pymongodb.shitfaces.find_one({"_id": ObjectId(record_id)}, filter)

    if not row:
        return False

    return row


def update_shitface_record_pymongo(record_id, data: dict):
    debugLog(f'In update_shitface_pymongo record ID is {record_id}')

    if not pymongodb:
        print("returning false")
        return False

    filter = {"$set": data}

    result = pymongodb.shitfaces.update_one({"_id": ObjectId(record_id)}, filter)

    return bool(result)


@celery.task(name="process_image")
def create_task(record_id, drawRectangle: bool):
    document = get_shitface_record_pymongo(record_id, True)

    if not document:
        return False

    decoded = document["original_file_contents"]
    shitfaced_file_contents = process_image(decoded, drawRectangle=drawRectangle)

    if not shitfaced_file_contents:
        raise Exception('Invalid dimensions or image format.')

    result = update_shitface_record_pymongo(record_id, {'shitfaced_file_contents': shitfaced_file_contents.getvalue()})

    if not result:
        raise Exception('Could not save the shitfaced file to the DB for some reason')

    return record_id
