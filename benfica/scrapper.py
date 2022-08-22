"""
Signal telegram channel a new game has come out

@author Miguel C. Matos
"""
import os
import sys
import requests
import re
import telegram

from datetime import datetime
from bs4 import BeautifulSoup
from telegram.message import Message


def get_page(uri: str) -> BeautifulSoup:
    """Get the html page and return a BeautifulSoup representation of it"""
    with requests.get(uri) as r:
        return BeautifulSoup(r.text, "html.parser")


def parse_page(page: BeautifulSoup) -> dict:
    """Parse the page and return its information"""
    last_game = (
        page.find_all("div", {"class": "sapomedia images"})[-1].find_all("div")[-1].text
    )
    game_date = last_game[:10]
    match = re.findall(
        r"([\d\wÀ-ÿ][\w\s\dÀ-ÿ]*[\d\wÀ-ÿ])\s-\s([\d\wÀ-ÿ][\w\d\sÀ-ÿ]*[\d\wÀ-ÿ])\svs\s([\d\wÀ-ÿ][\d\s\wÀ-ÿ]*[\d\wÀ-ÿ]).*\(.*\)",
        last_game,
    )
    if not match:
        sys.exit(0)
    match = match[0]
    competition = match[0]
    home_team = match[1]
    away_team = match[2]
    return {
        "date": game_date,
        "competition": competition,
        "home_team": home_team,
        "away_team": away_team,
    }


def generate_text(info: dict) -> str:
    """Create a message based on the info information"""
    date = info["date"]
    home_team = info["home_team"]
    away_team = info["away_team"]
    return f"O jogo {home_team} vs {away_team} ({date}) já se encontra disponível!"


def send_message(message: str) -> Message:
    """Send a message to a telegram chat

    Args:
        message (str): Message to send

    Raises:
        ValueError: Raised if BOT_TOKEN is not defined
        ValueError: Raised if CHAT_ID is not defined

    Returns:
        Message: Returns the value of the sent message
    """
    # load environmental variables
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("The value of BOT_TOKEN is not defined")
    CHAT_ID = os.environ.get("CHAT_ID")
    if not CHAT_ID:
        raise ValueError("The value of the CHAT_ID is not defined")

    bot = telegram.Bot(BOT_TOKEN)

    return bot.send_message(chat_id=CHAT_ID, text=message)


if __name__ == "__main__":
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CHAT_ID = os.environ.get("CHAT_ID")
    last_file = sys.argv[1] if len(sys.argv) > 1 else "last.txt"
    page = get_page("http://www.ternaalmaachamaimensa.pw/2022/07/epoca-202223.html")
    parsed_page = parse_page(page)
    last = open(last_file).read()[:10]
    if last < parsed_page["date"]:
        msg = generate_text(parsed_page)
        send_message(msg)
        open(last_file, "w").write(parsed_page["date"])
    else:
        print(datetime.now(), "-", "Não há novos jogos")
