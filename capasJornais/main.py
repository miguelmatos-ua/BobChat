import requests
import telegram
import sys
from bs4 import BeautifulSoup
from datetime import datetime
import time


BOT_TOKEN = sys.argv[1]  # Bot token and chat id passed with the command line
CHAT_ID = sys.argv[2]

bot = telegram.Bot(BOT_TOKEN)  # create instance of a telegram bot


uri_base = "https://www.vercapas.com/capa/{}.html"

uris = [
    ("correio-da-manha", "Correio da Manhã"),
    ("jornal-de-noticias", "Jornal de Notícias"),
    ("publico", "Público"),
    ("diario-de-noticias", "Diário de Notícias"),
    ("i", "Jornal i"),
    ("o-jogo", "O Jogo"),
    ("record", "Record"),
    ("a-bola", "A Bola"),
    ("expresso", "Expresso"),
]

imgs = []

today = datetime.today()
day = f"0{today.day}"[-2:]  # make 7 -> 07 but keep 12 -> 12
month = f"0{today.month}"[-2:]
print(day, month)

i = 0
for uri, name in ((uri_base.format(r), name) for r, name in uris):
    with requests.get(uri) as r:
        content = r.content

    soup = BeautifulSoup(content, features="html.parser")
    # find url of the newspaper cover
    img = soup.find("img", attrs={"alt": name}).attrs["src"]
    if datetime.today().strftime("%Y-%m-%d") not in img:
        # Don't send covers from past days
        continue
    print(name, img)
    imgs.append(telegram.InputMediaPhoto(img, caption=f"Capas de jornais do dia {day}/{month}" if i == 0 else ''))
    i += 1

# caption needs to be only on first element of the image or it won't work
# imgs[0].caption = f"Capas de jornais do dia {day}/{month}"

retries = 5
done = False
for i in range(retries, 0, -1):
    try:
        bot.send_media_group(CHAT_ID, media=imgs)  # send telegram message
        done = True
    except:
        done = False
    if done:
        break
    else:
        time.sleep(1)
