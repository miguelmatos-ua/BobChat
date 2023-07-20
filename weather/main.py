import requests
import os
import telegram
import sys
import time

# load environmental variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("The value of BOT_TOKEN is not defined")
CHAT_ID = os.environ.get("CHAT_ID")
if not CHAT_ID:
    raise ValueError("The value of the CHAT_ID is not defined")

bot = telegram.Bot(BOT_TOKEN)


def main():
    """Fetch weather for Aveiro"""
    img_name = "t.png"
    for i in range(5):
        try:
            print("Attempt", i + 1)
            with requests.get("https://wttr.in/Aveiro.png?1&m", stream=True) as r:
                with open(img_name, "wb") as im:
                    for chunk in r.iter_content(1024):
                        im.write(chunk)
            bot.send_photo(chat_id=CHAT_ID, photo=open(img_name, "rb"))
            break
        except Exception as e:
            print("error sending photo:", e)
            time.sleep(1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
