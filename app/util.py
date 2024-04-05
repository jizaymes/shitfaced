import os
import config

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def get_emoji_list(use_web_path: bool = False):
    emoji_list = []

    for emoji in os.listdir(config.EMOJI_FILE_PATH):
        if allowed_file(emoji):
            if use_web_path:
                emoji_list.append(f"{config.EMOJI_WEB_PATH}/{emoji}")
            else:
                emoji_list.append(emoji)

    return emoji_list

