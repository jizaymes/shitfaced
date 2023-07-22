from bson.objectid import ObjectId
from pymongo import MongoClient

from rich import print
import datetime

import config


class ShitfaceDB:
    db = None
    _mongo_client = None

    def __init__(self):
        self.setup_mongo()

    def setup_mongo(self):
        self._mongo_client = MongoClient(config.MONGODB_URL, serverSelectionTimeoutMS=config.MONGO_SERVER_SELECTION_TIMEOUT)
        mydb = self._mongo_client.shitfaced
        self.db = mydb.shitfaces

    def create_shitface_record(self, original_file_hash: str, original_file_name: str, original_file_content_type: str, http_info: dict):
        if self._mongo_client is None:
            return False

        record = {
            'http_info': http_info,
            'create_date': datetime.datetime.now(),
            'original_file_name': original_file_name,
            'original_file_content_type': original_file_content_type,
            'original_file_hash': original_file_hash,
            'original_file_url': '',
            'original_file_info': '',

            'overlay_image': '',

            'processed_file_name': '',
            'processed_file_content_type': '',
            'processed_file_hash': '',
            'processed_file_url': '',
            'processed_file_info': '',
        }

        row = self.db.insert_one(record)

        if not row:
            return False

        self.debugLog(f"I just created a shitface! {row.inserted_id}")

        return row.inserted_id

    def update_shitface_record(self, id, data: dict):
        self.debugLog(f'In update_shitface_record() : id is {id}')

        if self._mongo_client is None:
            return False

        updates = {"$set": data}

        self.debugLog(f"About to update {updates}")
        row = self.db.update_one({"_id": ObjectId(id)}, updates)
        if not row:
            return False

        return row

    def image_exists(self, file_hash, selected_emoji: str):
        self.debugLog(f"In image_exists for ({file_hash}, {selected_emoji})")

        if self._mongo_client is None:
            return False

        filters = {}

        query = {"$or": [{
            "original_file_hash": file_hash,
            }, {
            "processed_file_hash": file_hash,
            }],
            "$and": [{
                "overlay_image": selected_emoji,
            }]
        }
        row = self.db.find_one(query, filters)

        if not row:
            self.debugLog(f"image_exists is False. Didntfind anything for {file_hash}")
            return False

        # self.debugLog(f"Image exists about to return {row['_id']}")
        return row['_id']

    def get_shitface_record(self, record_id, filters: dict = None):
        self.debugLog(f'In get_shitface_record. id is {record_id}')

        if self._mongo_client is None:
            return False

        query = {"_id": ObjectId(record_id)}

        row = self.db.find_one(query, filters)

        if not row:
            self.debugLog("Leaving get_shitface_record empty handed. No record found")
            return False

        return row

    def disconnect_mongo(self):
        if self._mongo_client is not None:
            self._mongo_client.close()

    def debugLog(self, msg):
        print(f"{msg}") if config.DEBUG else False
