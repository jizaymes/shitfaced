import os
from typing import Optional, List
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from shitfaced import debugLog


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


async def get_shitface_record(id, db: AsyncIOMotorClient = None):
    debugLog(f'In shitface record ID is {id}')

    if not db:
        return False

    coll = db.get_collection('shitfaces')

    row = await coll.find({"_id": str(id)})

    if not row:
        return False

    print(row)
    return row
