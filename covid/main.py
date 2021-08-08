"""
Web scraper to get latest pdf and send telegram message with the pdf and its data

@author: Miguel C. Matos
"""
import os
import sys
import telegram
import requests
import pdfplumber

from datetime import datetime
from bs4 import BeautifulSoup


last_txt = "last.txt"
if not os.path.exists(last_txt):
    last_txt = "covid/last.txt"

def latest_day():
    with open(last_txt) as last:
        day = last.readlines()[-1]
    return datetime.strptime(day, "%d/%m/%Y")


def web_scrap(day):
    """Find the latest pdf from Min. Saúde Website"""
    uri = "https://covid19.min-saude.pt/relatorio-de-situacao/"
    date=day.strftime("%Y%m%d")
    with requests.get(uri) as r:
        soup = BeautifulSoup(r.text, "lxml")

        for a in soup.find_all("a"):
            link = a.get("href")
            if link and "DGS_boletim" in link and date in link and link.endswith(".pdf"):
                return link



def extract_data(pdf_link):
    with open("today.pdf", "wb") as pdf_file:
        r = requests.get(pdf_link)

        for chunk in r.iter_content(2048):
            pdf_file.write(chunk)
        
        r.close()

    p = pdfplumber.open("today.pdf")
    # first page data
    page = p.pages[0]

    # Crops 30% of the page
    left_page = page.crop((0, 0, 0.3 * float(page.width), page.height))

    # Split string by the line breaks
    words_lst = left_page.extract_text().split("\n")
    # Reverse the list
    words_lst.reverse()

    words_lst = list(filter(lambda x: x != " ", words_lst))  # remove empty spaces 
    print(words_lst)

    data = dict()
    for i, s in enumerate(words_lst):
        if "CONFIRMADOS" in ''.join(filter(lambda x: x != " ", s)):
            new_data = [int('0' + ''.join([y for y in x if y.isnumeric()]))
                        for x in words_lst[i + 1].split("+")]
            if len(new_data) < 2:
                new_data.append('0')
            data['confirmados'] = {'total': new_data[0], 'novos': new_data[1]}
        elif "ÓBITOS" in ''.join(filter(lambda x: x != " ", s)):
            new_data = [int('0' + ''.join([y for y in x if y.isnumeric()]))
                        for x in words_lst[i + 1].split("+")]
            if len(new_data) < 2:
                new_data.append('0')
            data['óbitos'] = {'total': new_data[0], 'novos': new_data[1]}
        elif "RECUPERADOS" in ''.join(filter(lambda x: x != " ", s)):
            new_data = [int('0' + ''.join([y for y in x if y.isalnum()]))
                        for x in words_lst[i + 1].split("+")]
            if len(new_data) < 2:
                new_data.append('0')
            data['recuperados'] = {'total': new_data[0], 'novos': new_data[1]}

    # Aveiro stats
    is_aveiro = True
    try:
        page = p.pages[3]
    except IndexError:
        is_aveiro = False
    
    if is_aveiro:
        aveiro = None
        # iterate to find Aveiro stats
        for lines in page.extract_text().split("\n"):
            if "Aveiro" in lines:
                line = lines.split(" ")
                aveiro = line[line.index("Aveiro") + 1]
                break
        
        data["aveiro"] = aveiro

    # Internados values
    page = p.pages[0]
    internados_page = page.crop((0, 0.84 * float(page.height), 0.2 * float(page.width), 0.9 * float(page.height)))
    uci_page = page.crop((0.22 * float(page.width), 0.84 * float(page.height), page.width, 0.9 * float(page.height)))

    data["internados"] = __extract_vals(internados_page)
    data["uci"] = __extract_vals(uci_page)

    return data


def __extract_vals(page):
    print([x for x in page.extract_text().split("\n") if x != " "])
    vals = [x for x in page.extract_text().split("\n") if x != " "][0]
    char = "-" if "-" in vals else "+"
    m = [x.replace(" ", "") for x in vals.split(char)]
    if m[1] == '':
        m[1] = "0"
    return int(m[0]), char + m[1]


def build_msg(data, day):
    aveiro = data.get("aveiro")
    aveiro_string = '' if aveiro is None else f'\n\nAveiro: {aveiro}'
    internados = data.get("internados")
    uci = data.get("uci")

    internados_str = ""
    if uci is not None and internados is not None:
        internados_str = f"\n\nInternados: {internados[0]} | {internados[1]}\n" \
                         f"UCI: {uci[0]} | {uci[1]}"

    msg = f"<b>{day}</b>\n" \
          f"Novos Casos: {data['confirmados']['total']} | +{data['confirmados']['novos']}\n" \
          f"Óbitos: {data['óbitos']['total']} | +{data['óbitos']['novos']}\n" \
          f"Recuperados: {data['recuperados']['total']} | +{data['recuperados']['novos']}" \
          + internados_str + aveiro_string

    return msg
    


def update_last():
    with open(last_txt, "w") as last:
        last.write(datetime.today().strftime("%d/%m/%Y"))


if __name__ == "__main__":
    BOT_TOKEN = sys.argv[1]
    CHAT_ID = sys.argv[2]

    bot = telegram.Bot(BOT_TOKEN)

    last_day = latest_day()

    if datetime.today() == last_day:
        # message already sent. end program
        print("Message already sent today")
        sys.exit(0)
    
    # Message hasn't been sent yet
    today = datetime.today()
    link = web_scrap(today)
    data = extract_data(link)
    build_msg(data, today.strftime("%d/%m/%Y"))
    update_last()
