import requests
import telegram
import sys
from bs4 import BeautifulSoup
from datetime import datetime


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
    ("a-bola", "A Bola"),
    ("record", "Record"),
    ("o-jogo", "O Jogo"),
    ("expresso", "Expresso"),
]

imgs = []


for uri, name in ((uri_base.format(r), name) for r, name in uris):
    content = requests.get(uri).content
    soup = BeautifulSoup(content, features="html.parser")
    # find url of the newspaper cover
    img = soup.find("img", attrs={"alt": name}).attrs["src"]
    print(name, img)
    imgs.append(telegram.InputMediaPhoto(img))

today = datetime.today()
day = f"0{today.day}"[-2:]  # make 7 -> 07 but keep 12 -> 12
month = f"0{today.month}"[-2:]
print(day, month)

# caption needs to be only on first element of the image or it won't work
imgs[0].caption = f"Capas de jornais do dia {day}/{month}"

bot.send_media_group(CHAT_ID, media=imgs)  # send telegram message
