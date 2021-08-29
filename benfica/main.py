import requests
import sys
from datetime import date, datetime
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

        if hour.text:
            # parse day and hour to an instance of datetime
            game_date = datetime.strptime(f"{date.text} {hour.text}", "%d/%m %H:%M")
        elif date.text:
            # there is no hour but there is a date
            game_date = datetime.strptime(f"{date.text}", "%d/%m")
        else:
            # there is no hour nor date
            # therefore this game is not necessary to
            # be returned
            continue

        # year is 1900, change to today's year
        game_date = game_date.replace(year=datetime.today().year)

        day = game_date.date()  # just the date without the time

        games[day] = dict()
        games[day]["date"] = game_date

        home_team = tr.find("td", {"class": "text home"})
        away_team = tr.find("td", {"class": "text away"})

        tv = tr.find("td", {"class": "double right"})
        if tv and tv.img:
            # if there is a class named "double right" that has an image
            tv = tv.img["title"]

            games[day]["tv"] = tv

        games[day]["home_team"] = home_team.text
        games[day]["away_team"] = away_team.text
    
    return games


def build_message(game):
    print(game)
    ...


def main(team_id=4):
    uri_zz = f"https://www.zerozero.pt/team.php?id={team_id}"
    soup = download_page_zz(uri_zz)
    games = extract_games(soup)

    today = datetime.today().date()

    if today not in games.keys():
        # exit if there is no game today
        sys.exit(0)

    print(games, today)
    build_message(games[today])


if __name__ == "__main__":
    main()
