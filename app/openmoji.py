import json
from rich import print

from database import EmojiDB

FILE="openmoji.json"

emojidb = EmojiDB()

def load_emojis():
    with open(FILE, "r") as hwnd:
        contents = json.load(hwnd)

    for item in contents:
        # print(item)
        # print(item['hexcode'])
        # print(item['group'])
        # print(item['subgroups'])
        # print(item['skintone'])
        # print(item['skintone_base_emoji'])

        # Doesn't exist, add a new
        if not emojidb.get_emoji_record(item['emoji']):
            if new_id := emojidb.create_emoji_record(item):
                print(f"New Emoji ID for {item['emoji']} is {new_id}")


if __name__ == "__main__":
    # load_emojis()
    # print(emojidb.get_count())
    # print(emojidb.get_count("smileys-emotion"))
    # print(emojidb.get_group_counts())
    # print(emojidb.get_groups())
    print(emojidb.get_emoji_record("😅"))
