from PIL import Image, ImageDraw
from pathlib import Path
import face_recognition
from io import BytesIO
from rich import print

OVERLAY_IMAGE = Path('./poop.png')
IMAGE_MODE = "RGBA"
OUTPUT_FORMAT = 'PNG'
RESIZE_SCALE = .1

DEBUG = False
DEBUG = True



def debugLog(msg):
    print(f"{msg}") if DEBUG else False


def get_faces_from_image(infile):
    image = face_recognition.load_image_file(BytesIO(infile))
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


def process_image(infile, drawRectangle=False):

    # Convert the incoming image to a Pillow image in memory, and conver to the right mode
    infile_image = Image.open(BytesIO(infile)).convert(IMAGE_MODE)

    h, w = infile_image.size
    debugLog(f"h {h} w {w}")
    if h < 150 and w < 150:
        return False

    # Load the overlay image and convert it to the right mode
    overlay_image = Image.open(OVERLAY_IMAGE).convert(IMAGE_MODE)

    face_locations, face_encodings = get_faces_from_image(infile)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        debugLog("-- New Face {{")
        debugLog(f"Top {top}, Right {right}, Bottom {bottom}, Left {left}")

        tt, rr, bb, ll = apply_scaling(top, right, bottom, left, RESIZE_SCALE)

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
    infile_image.save(img_byte_arr, format=OUTPUT_FORMAT)

    return img_byte_arr
