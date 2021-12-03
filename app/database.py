import os

from io import BytesIO
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from shitfaced import debugLog
from rich import print, inspect


def setup_mongo() -> AsyncIOMotorClient:
    db: AsyncIOMotorClient = None

    debugLog("Setting up Mongo")
    db = AsyncIOMotorClient(os.environ.get("MONGODB_URL", "mongodb://localhost:27017"))
    print(db)
    return db["shitfaced"]


db = setup_mongo()


async def shutdown_mongo():
    debugLog("Shutting down Mongo")
    if db:
        db.client.close()


async def create_shitface(file_bytes: bytes, file_name: str, content_type: str, http_info: dict, db: AsyncIOMotorClient = None):
    if not db:
        return False

    record = {
        'original_file_name': file_name,
        'content_type': content_type,
        'http_info': http_info,
        'original_file_contents': file_bytes,
        'shitfaced_file_contents': '',
    }

    coll = db.get_collection('shitfaces')

    row = await coll.insert_one(record)

    if not row:
        return False

    return row.inserted_id


async def get_shitface_image(id, db: AsyncIOMotorClient = None):
    debugLog(f'In get_shitface_image record ID is {id}')

    if not db:
        print("No db, returning false")
        return False

    row = await get_shitface_record(id, {'shitfaced_file_contents': 1}, db)

    if not row:
        print("Returning False")
        return False

    return row["shitfaced_file_contents"]


async def get_shitface_record(id, filters: dict = None, db: AsyncIOMotorClient = None):
    debugLog(f'In shitface record ID is {id}')

    if not db:
        return False

    coll = db.get_collection('shitfaces')

    query = {"_id": ObjectId(id)}

    row = await coll.find_one(query, filters)

    if not row:
        return False

    return row


def update_shitface_record(id, data: dict, db: AsyncIOMotorClient = None):
    debugLog(f'In update_shitface record ID is {id}')

    if not db:
        return False

    coll = db.get_collection('shitfaces')

    row = coll.replace_one({"_id": id}, **data)

    if not row:
        return False

    return row
