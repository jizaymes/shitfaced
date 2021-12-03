import os
from shitfaced import setup_celery, process_image, debugLog

from pymongo import MongoClient
from bson.objectid import ObjectId

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

    print(f"Returning {bool(result)}")
    return bool(result)


@celery.task(name="process_image")
def create_task(record_id, drawRectangle: bool):
    print("Entering Create Task")
    document = get_shitface_record_pymongo(record_id, True)

    if not document:
        return False

    decoded = document["original_file_contents"]
    shitfaced_file_contents = process_image(decoded, drawRectangle=drawRectangle)
    print(f"Size of shitfaced_file is {len(shitfaced_file_contents.getvalue())}")
    result = update_shitface_record_pymongo(record_id, {'shitfaced_file_contents': shitfaced_file_contents.getvalue()})

    if not result:
        return False

    print(f"Create Task has result of: {record_id}")
    return record_id
