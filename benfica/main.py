import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup


def download_page_zz(uri):
    """Get the page from the ZeroZero website to web scrap

    Args:
        uri (str): Url of the page

    Returns:
        BeautifulSoup: Return a BeautifulSoup instance of the web page
    """
    page = requests.get(uri).content  # html page of ZeroZero
    return BeautifulSoup(page, features="html.parser")


def extract_games(soup: BeautifulSoup) -> dict:
    game_box = soup.find("div", {"id": "team_games"})  # find the div with the class team_games
    games = dict()
    for tr in game_box.find_all("tr"):  # for all the lines (games) in the table
        date = tr.find("td", {"class": "date"})  # find the date column
        hour = date.find_next()  # the hour column is besides the date

        home_team = tr.find("td", {"class": "text home"})
        away_team = tr.find("td", {"class": "text away"})
        print(date.text, hour.text, home_team.text, away_team.text)
    ...


def main(team_id=4):
    uri_zz = f"https://www.zerozero.pt/team.php?id={team_id}"
    soup = download_page_zz(uri_zz)
    extract_games(soup)


if __name__ == "__main__":
    main()