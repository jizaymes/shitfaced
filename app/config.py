import os

# Debug Logging
DEBUG = os.environ.get('DEBUG', False)

MONGODB_URL = os.environ.get('MONGODB_URL', "mongodb://mongo:27017")
MONGO_SERVER_SELECTION_TIMEOUT = os.environ.get("MONGO_SERVER_SELECTION_TIMEOUT", 5000)

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', ["http://localhost:8000"])
ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', ['png', 'jpg', 'jpeg', 'gif'])
MAX_ALLOWED_FILESIZE = os.environ.get('MAX_ALLOWED_FILESIZE', 4194304)

EMOJI_FILE_PATH = "static/emojis"
EMOJI_WEB_PATH = "emojis"
DEFAULT_OVERLAY_IMAGE = 'poop.png'

DRAW_RECTANGLE = False
IMAGE_MODE = "RGBA"
OUTPUT_FORMAT = 'PNG'
RESIZE_SCALE = .1

# REQUIRED ENVIRONMENT INFORMATION IN shitfaced.env

# For initial pipeline
INCOMING_OBJ_STORAGE_CONFIG = {
    "aws_access_key_id": os.environ.get('INCOMING_ACCESS_KEY'),
    "aws_secret_access_key": os.environ.get('INCOMING_SECRET_KEY'),
    "endpoint_url": os.environ.get('INCOMING_BUCKET_URL'),
}
INCOMING_BUCKET = os.environ.get('INCOMING_BUCKET')

# For processed images
PROCESSED_OBJ_STORAGE_CONFIG = {
    "aws_access_key_id": os.environ.get('PROCESSED_ACCESS_KEY'),
    "aws_secret_access_key": os.environ.get('PROCESSED_SECRET_KEY'),
    "endpoint_url": os.environ.get('PROCESSED_BUCKET_URL'),
}
PROCESSED_BUCKET = os.environ.get('PROCESSED_BUCKET')
