import requests
import os
import telegram
import sys

# load environmental variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("The value of BOT_TOKEN is not defined")
CHAT_ID = os.environ.get("CHAT_ID")
if not CHAT_ID:
    raise ValueError("The value of the CHAT_ID is not defined")


with open("benfica/last_abola.txt", "r") as last:
    last_news = last.readlines()
    last_news_date = last_news[-1].rstrip()

bot = telegram.Bot(BOT_TOKEN)

uri = "https://www.abola.pt/_next/data/4IE9STwfE9_nnqYObLZ9x/futebol/benfica-450.json?teamSlugId=benfica-450"

news = requests.get(uri).json()

benfica_news = news['pageProps']['tagArticlesData']['data']

processed_ids = set()

for news in benfica_news:
    title = news['title']
    subtitle = news['subtitle']

    date = news['id'][:12]

    if int(date) <= int(last_news_date[:12]):
        continue

    print('Date Not Passed:', date, int(last_news_date[:12]))
    processed_ids.add(int(date))
    if subtitle is None:
        subtitle = ""

    date_published = news['updated_at'].split('T')
    message = f"{title}" + (f"\n{subtitle}" if subtitle else "") + f" ({date_published[0]} às {date_published[1][:5]})"

    image = news['image']['data']['urls']['uploaded']['embed']
    bot.send_photo(chat_id=CHAT_ID, photo=image, caption=message)
    
if not processed_ids:
    sys.exit(0)

m = max(processed_ids)

with open("benfica/last_abola.txt", "w") as last:
    last.write(f"{m}\n")