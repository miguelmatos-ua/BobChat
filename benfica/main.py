import requests
import sys
import os
import telegram

from datetime import date, datetime, timedelta
from deprecated import deprecated
from bs4 import BeautifulSoup
from telegram.message import Message
from todoist_api_python.api import TodoistAPI


def download_page_zz(uri: str):
    """Get the page from the ZeroZero website to web scrap

    Args:
        uri (str): Url of the page

    Returns:
        BeautifulSoup: Return a BeautifulSoup instance of the web page
    """
    page = requests.get(uri).content  # html page of ZeroZero
    return BeautifulSoup(page, features="html.parser")


def extract_games(soup: BeautifulSoup):
    """Web Scrap the previous and next games

    Args:
        soup (BeautifulSoup): Instance of the html page of ZeroZero

    Returns:
        dict: Dictionary with the information of the previous and next games
    """
    # find the div with the class team_games
    game_box = soup.find("div", {"id": "team_games"})
    games = dict()
    if game_box is None:
        return {}
    # for all the lines (games) in the table
    for tr in game_box.find_all("tr"):
        date = tr.find("td", {"class": "date"})  # find the date column
        hour = date.find_next()  # the hour column is besides the date

        if hour.text:
            # parse day and hour to an instance of datetime
            game_date = datetime.strptime(
                f"{date.text} {hour.text}", "%d/%m %H:%M")
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


def build_message(game: dict, team_name: str):
    """Build the message to be sent

    Creates a message based on the game, with the date time and the team that they're playing

    Args:
        game (dict): Game from which the message will be built
        team_name (str): Name of the team

    Returns:
        str: Returns the message that was built

    """

    date: datetime = game["date"]

    hour = ("0" + str(date.hour))[-2:]
    minutes = ("0" + str(date.minute))[-2:]

    time = f"{hour}:{minutes}h"

    message = f"""Hoje joga o {team_name}.
Às {time}.
{game["home_team"]} vs. {game["away_team"]}"""
    return message


@deprecated(reason="Support for the 'create calendar' feature is dropped.")
def create_calendar(home_team, away_team, competition, time: datetime):
    """
    Create a calendar file to add to Google Calendar
    """
    start = time.strftime("%Y%m%dT%H%M%SZ")
    end = time + timedelta(minutes=45)
    end = end.strftime("%Y%m%dT%H%M%SZ")
    with open("calendar.ics", "w") as calendar:
        calendar.write("BEGIN:VCALENDAR\n")
        calendar.write("VERSION:2.0\n")
        calendar.write("PRODID:-//hacksw/handcal//NONSGML v1.0//EN\n")
        calendar.write("BEGIN:VEVENT\n")
        calendar.write(f"DTSTART:{start}\n")
        calendar.write(f"DTEND:{end}\n")
        calendar.write(f"SUMMARY:{home_team} vs. {away_team}\n")
        calendar.write(f"DESCRIPTION:{competition}\n")
        calendar.write("END:VEVENT\n")
        calendar.write("END:VCALENDAR\n")

    return "calendar.ics"


def send_message(message) -> Message:
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

    # add file to the message
    if os.path.exists("calendar.ics"):
        with open("calendar.ics", "rb") as calendar:
            return bot.send_document(CHAT_ID, calendar, caption=message)

    return bot.send_message(chat_id=CHAT_ID, text=message)


def add_todoist(game: dict):
    """Create a todoist task.

    Creates a `todoist` task to edit the video after a Benfica game.

    Args:
        game (dict): Game from which the task will be created

    Raises:
        ValueError: Raised if TODOIST_TOKEN is not defined

    Returns:
        None: Returns nothing
    """
    TODOIST_TOKEN = os.environ.get("TODOIST_TOKEN")
    if not TODOIST_TOKEN:
        raise ValueError("The value of TODOIST_TOKEN is not defined")

    # create a todoist task
    todoist = TodoistAPI(TODOIST_TOKEN)
    # get project id
    project_id = [p for p in todoist.get_projects() if p.name == "Personal"][0].id

    labels = [l.id for l in todoist.get_labels() if l.name == "entertainment" or l.name == "personal_projects"]

    message = f"""Editar {game["home_team"]} vs. {game["away_team"]} ⚽"""

    todoist.add_task(content=message, project_id=project_id, label_ids=labels, priority=2, due_string="Tomorrow")


def main(team_id=4, team_name="Benfica"):
    uri_zz = f"https://www.zerozero.pt/team.php?id={team_id}"
    soup = download_page_zz(uri_zz)
    games = extract_games(soup)

    today = datetime.today().date()

    if today not in games.keys():
        # exit if there is no game today
        sys.exit(0)

    msg = build_message(games[today], team_name)

    print(send_message(msg))

    if team_name == "Benfica":
        print("Adding todoist task")
        add_todoist(games[today])
        print("Todoist task added")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]), sys.argv[2])
    else:
        main()
