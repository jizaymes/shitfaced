from PIL import Image, ImageDraw, ExifTags, UnidentifiedImageError
from io import BytesIO
from rich import print

import face_recognition
import os

import config

from pillow_heif import register_heif_opener

register_heif_opener()

MIN_HEIGHT = 150
MIN_WIDTH = 150
MAX_HEIGHT = 4000
MAX_WIDTH = 4000


def debugLog(msg):
    print(f"{msg}") if config.DEBUG else False




def get_faces_from_image(infile):
    image = face_recognition.load_image_file(infile)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    return face_locations, face_encodings




def apply_scaling(top, right, bottom, left, scale: float):
    # Dimensions of the face that we found
    height = round(right - left)
    width = round(bottom - top)
    debugLog(f"Old {height} {width}")

    aspect_ratio = width / height

    new_height = round(height * (1 + scale))
    new_width = round(width * (1 + scale))
    debugLog(f"New {new_height} {new_width}")

    # Apply scale to the bounding coordinates so our overlay can be bigger..if scale says so
    tt = round(top - (new_height - height))
    rr = round((left + new_width) * aspect_ratio)
    bb = round((top + new_height) * aspect_ratio)
    ll = round(left - (new_width - width))

    return tt, rr, bb, ll


def validate_image(infile_base):
    # Convert the incoming image to a Pillow image in memory, and conver tto the right mode
    try:
        infile_image = Image.open(BytesIO(infile_base))
    except UnidentifiedImageError:
        return {'error': 'Sorry, image in not valid'}

    h, w = infile_image.size

    if h < MIN_HEIGHT and w < MIN_WIDTH:
        debugLog(f"h {h} w {w}")
        return {'error': 'Sorry, image is too small to process'}

    if h > MAX_HEIGHT and w > MAX_WIDTH:
        debugLog(f"h {h} w {w}")
        return {'error': 'Sorry, image is too large to process'}

    return infile_image


def needs_rotating(infile_exif_data):
    if infile_exif_data:
        for key, val in infile_exif_data:
            if key in ExifTags.TAGS:
                debugLog(f'{ExifTags.TAGS[key]}:{val}')
                # TileWidth:512
                # TileLength:512
                # ResolutionUnit:2
                # ExifOffset:248
                # Make:Apple
                # Model:iPhone 13 Pro
                # Software:16.5.1
                # Orientation:6
                # DateTime:2023:07:15 14:27:50
                # YCbCrPositioning:1
                # XResolution:72.0
                # YResolution:72.0
                # HostComputer:iPhone 13 Pro

                if ExifTags.TAGS[key] == "Orientation" and val == 6:
                    debugLog("NEEDS TO BE ROTATED")  # IOS ?
                    return val

    return False


def generate_shitface(infile, overlay_image: str, drawRectangle: bool = False):

    # Try to validate the image and then error if need be
    infile_base = validate_image(infile)

    if type(infile_base) is dict:
        return infile_base

    # Load EXIF data if its there
    infile_exif_data = infile_base.getexif().items()

    # Determine if we need to rotate
    orientation = needs_rotating(infile_exif_data)

    # Convert to a PNG
    infile_image = infile_base.convert(config.IMAGE_MODE)

    if orientation is not False:
        rotation = 0

        if orientation == 6:  # IOS
            rotation = -90

        debugLog("About to rotate")

        if rotation != 0:
            infile_image = infile_image.rotate(rotation)
            debugLog("Did rotate that")
    else:
        debugLog("Doesn't need rotating")

    # Load the overlay image and convert it to the right mode
    overlay_image = f"{config.EMOJI_FILE_PATH}/{overlay_image}"
    overlay_image = Image.open(overlay_image).convert(config.IMAGE_MODE)

    image_bytes = BytesIO()

    infile_image.save(image_bytes, format=config.OUTPUT_FORMAT)

    face_locations, face_encodings = get_faces_from_image(image_bytes)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        debugLog("-- New Face {{")
        debugLog(f"Top {top}, Right {right}, Bottom {bottom}, Left {left}")

        tt, rr, bb, ll = apply_scaling(top, right, bottom, left, config.RESIZE_SCALE)

        debugLog("  New face params")
        debugLog(f"Top {tt}, Right {rr}, Bottom {bb}, Left {ll}")

        # resize our overlay image to match this size
        tmp_overlay = overlay_image.resize((rr - ll, bb - tt))

        # If we're in debug mode/drawRectangle=True
        if drawRectangle:
            draw = ImageDraw.Draw(infile_image)
            draw.rectangle(((ll, tt), (rr, bb)), outline=(0, 255, 0))

        # Apply the overlay
        infile_image.paste(tmp_overlay, (ll, tt), tmp_overlay)

        debugLog("}} End Face")

    img_byte_arr = BytesIO()

    infile_image.save(img_byte_arr, format=config.OUTPUT_FORMAT)

    return img_byte_arr
