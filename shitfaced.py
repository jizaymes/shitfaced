from PIL import Image, ImageDraw
from pathlib import Path
import face_recognition
from rich import print
import io

OVERLAY_IMAGE = Path('./poop.png')
IMAGE_MODE = "RGBA"
OUTPUT_FORMAT = 'PNG'
RESIZE_SCALE = .05
# DEBUG = True
DEBUG = False


def debugLog(msg):
    print(f"{msg}") if DEBUG else False


def get_faces_from_image(infile):
    image = face_recognition.load_image_file(io.BytesIO(infile))
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    return face_locations, face_encodings


def process_image(infile, filename: str, drawRectangle=False):
    image = Image.open(io.BytesIO(infile))

    face_locations, face_encodings = get_faces_from_image(infile)

    infile_image = image.convert(IMAGE_MODE)
    overlay_image = Image.open(OVERLAY_IMAGE).convert(IMAGE_MODE)
    output_image = infile_image.copy()

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        debugLog("-- New Face {{")
        debugLog(f"Top {top}, Right {right}, Bottom {bottom}, Left {left}")

        # Dimensions of the face that we found
        height = round(right - left)
        width = round(bottom - top)

        debugLog(f"  Face Height, Weight ({height}, {width})")

        start_left = left
        start_top = top
        debugLog(f"  Starting X, Y ({start_left}, {start_top})")

        height = int((right - left) * (1 + RESIZE_SCALE))
        width = int((bottom - top) * (1 + RESIZE_SCALE))

        debugLog(f"  Updated Face Height, Weight ({height}, {width})")

        start_left = round(left - round(left * RESIZE_SCALE))
        start_top = round(top - round(top * RESIZE_SCALE))

        debugLog(f"  Updated X, Y ({start_left}, {start_top})")

        draw = ImageDraw.Draw(output_image) if drawRectangle else False

        ll = round(left * (1 - RESIZE_SCALE))
        tt = round(top * (1 - RESIZE_SCALE))
        rr = round(right * (1 + RESIZE_SCALE))
        bb = round(bottom * (1 + RESIZE_SCALE))
        debugLog(f"  New face params {ll}, {tt}, {rr}, {bb}")

        tmp_overlay = overlay_image.resize((rr - ll, bb - tt))

        draw.rectangle(((ll, tt), (rr, bb)), outline=(0, 255, 0)) if drawRectangle else False
        output_image.paste(tmp_overlay, (ll, tt), tmp_overlay)

        debugLog("}} End Face")

    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format=OUTPUT_FORMAT)
    return img_byte_arr
