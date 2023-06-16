import requests
import os
import telegram

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
    with requests.get("https://wttr.in/Aveiro.png?1&m", stream=True) as r:
        with open(img_name, "wb") as im:
            for chunk in r.iter_content(1024):
                im.write(chunk)
    bot.send_photo(chat_id=CHAT_ID, photo=open(img_name, "rb"))


if __name__ == "__main__":
    main()
