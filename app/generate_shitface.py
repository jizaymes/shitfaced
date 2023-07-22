from PIL import Image, ImageDraw
from io import BytesIO
from rich import print

import face_recognition
import os

import config


def debugLog(msg):
    print(f"{msg}") if config.DEBUG else False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def get_faces_from_image(infile):
    image = face_recognition.load_image_file(BytesIO(infile))
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    return face_locations, face_encodings


def get_emoji_list(use_web_path: bool = False):
    emoji_list = []

    for emoji in os.listdir(config.EMOJI_FILE_PATH):
        if allowed_file(emoji):
            if use_web_path:
                emoji_list.append(f"{config.EMOJI_WEB_PATH}/{emoji}")
            else:
                emoji_list.append(emoji)

    return emoji_list


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


def generate_shitface(infile, overlay_image: str, drawRectangle: bool = False):

    # Convert the incoming image to a Pillow image in memory, and conver tto the right mode
    infile_image = Image.open(BytesIO(infile)).convert(config.IMAGE_MODE)

    h, w = infile_image.size
    debugLog(f"h {h} w {w}")
    if h < 150 and w < 150:
        return False

    # Load the overlay image and convert it to the right mode
    overlay_image = f"{config.EMOJI_FILE_PATH}/{overlay_image}"
    debugLog(overlay_image)
    overlay_image = Image.open(overlay_image).convert(config.IMAGE_MODE)

    face_locations, face_encodings = get_faces_from_image(infile)

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
