"""
Web scraper to get latest pdf and send telegram message with the pdf and its data

@author: Miguel C. Matos
"""
import os
import sys
import telegram
import requests
import pdfplumber
import time

from datetime import datetime
from bs4 import BeautifulSoup


last_txt = "last.txt"
if not os.path.exists(last_txt):
    last_txt = "covid/last.txt"


def latest_day():
    with open(last_txt) as last:
        day = last.readlines()[-1].replace("\n", "")
    return datetime.strptime(day, "%d/%m/%Y")


def web_scrap(day):
    """Find the latest pdf from Min. Saúde Website"""
    uri = "https://covid19.min-saude.pt/relatorio-de-situacao/"
    date = day.strftime("%Y%m%d")
    with requests.get(uri) as r:
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a"):
            link = a.get("href")
            if link and "DGS_boletim" in link and date in link and link.endswith(".pdf"):
                return link


def get_from_dataset(day):
    """Find the latest data in the DSSG-PT dataset"""
    uri = "https://raw.githubusercontent.com/dssg-pt/covid19pt-data/master/data.csv"
    date = day.strftime("%d-%m-%Y")
    
    with requests.get(uri) as r:
        content = r.content.decode("utf8").splitlines()
        
    # get the last line of the content
    last_line = content[-1]
    # get the penultimate line to make the difference between the values
    second_line = content[-2]

    # split the line to separate all the csv values
    last_line = last_line.split(",")
    second_line = second_line.split(",")

    # get the last day, which is the first column value
    last_day = last_line[0]

    if last_day != date:
        # today's numbers haven't come out yet
        return None
    
    vals = dict()
    vals["confirmados"] = {'total': last_line[2], 'novos': last_line[11]}

    new_deaths = int(last_line[13]) - int(second_line[13])
    vals["óbitos"] = {'total': last_line[13], 'novos': str(new_deaths)}

    new_recovered = int(last_line[12]) - int(second_line[12])
    vals["recuperados"] = {'total': last_line[12], 'novos': str(new_recovered)}

    new_internados = int(last_line[14]) - int(second_line[14])
    if new_internados > 0:
        new_internados = '+' + str(new_internados)
    vals["internados"] = (last_line[14], new_internados)
    
    new_uci = int(last_line[15]) - int(second_line[15])
    if new_uci > 0:
        new_uci = '+' + str(new_uci)
    vals["uci"] = (last_line[15], new_uci)

    return vals



def extract_data(pdf_link):
    with open("relatório.pdf", "wb") as pdf_file:
        r = requests.get(pdf_link)

        for chunk in r.iter_content(2048):
            pdf_file.write(chunk)

        r.close()

    p = pdfplumber.open("relatório.pdf")
    # first page data
    page = p.pages[0]

    # Crops 30% of the page
    left_page = page.crop((0, 0, 0.3 * float(page.width), page.height))

    # Split string by the line breaks
    words_lst = left_page.extract_text().split("\n")
    # Reverse the list
    words_lst.reverse()

    words_lst = list(filter(lambda x: x != " ", words_lst)
                     )  # remove empty spaces
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
    internados_page = page.crop(
        (0, 0.84 * float(page.height), 0.2 * float(page.width), 0.9 * float(page.height)))
    uci_page = page.crop((0.22 * float(page.width), 0.84 *
                         float(page.height), page.width, 0.9 * float(page.height)))

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


def send_msg(msg, file="relatório.pdf"):
    if file and os.path.exists(file):
        retries = 5

        while retries > 0:
            try:
                return bot.send_document(chat_id=CHAT_ID, document=open(file, "rb"), caption=msg, parse_mode="HTML")
            except telegram.error.TimedOut:
                print("Timed out:", retries, "retries")
                time.sleep(1)
                retries -= 1

        msg += "\n<i>PDF sending timed out</i>"

    return bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")


def update_last():
    with open(last_txt, "w") as last:
        last.write(datetime.today().strftime("%d/%m/%Y"))


if __name__ == "__main__":
    BOT_TOKEN = sys.argv[1]
    CHAT_ID = sys.argv[2]

    bot = telegram.Bot(BOT_TOKEN)

    last_day = latest_day()

    if datetime.today().strftime("%d/%m") == last_day.strftime("%d/%m"):
        # message already sent. end program
        print("Message already sent today")
        sys.exit(0)

    # Message hasn't been sent yet
    today = datetime.today()
    try:
        link = web_scrap(today)
    except requests.exceptions.ConnectionError:
        print("Couldn't make the connection")
        link = None

    data = get_from_dataset(today)
    file_is_in = False
    if link is None and data is None:
        print("Report hasn't come out yet")
        sys.exit(0)
    if data is None:
        file_is_in = True
        data = extract_data(link)
    msg = build_msg(data, today.strftime("%d/%m/%Y"))
    send_msg(msg, file="relatório.pdf" if file_is_in else None)
    update_last()
