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
    # find the div with the class team_games
    game_box = soup.find("div", {"id": "team_games"})
    games = dict()
    # for all the lines (games) in the table
    for tr in game_box.find_all("tr"):
        date = tr.find("td", {"class": "date"})  # find the date column
        hour = date.find_next()  # the hour column is besides the date

        # parse day and hour to an instance of datetime
        game_date = datetime.strptime(f"{date.text} {hour.text}", "%d/%m %H:%M")

        # year is 1900, change to today's year
        game_date = game_date.replace(year=datetime.today().year)

        games[game_date] = dict()

        home_team = tr.find("td", {"class": "text home"})
        away_team = tr.find("td", {"class": "text away"})

        tv = tr.find("td", {"class": "double right"})
        if tv and tv.img:
            # if there is a class named "double right" that has an image
            tv = tv.img["title"]

            games[game_date]["tv"] = tv

        games[game_date]["home_team"] = home_team.text
        games[game_date]["away_team"] = away_team.text
    
    return games


def main(team_id=4):
    uri_zz = f"https://www.zerozero.pt/team.php?id={team_id}"
    soup = download_page_zz(uri_zz)
    games = extract_games(soup)

    print(games)


if __name__ == "__main__":
    main()
