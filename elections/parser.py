"""
Generate a file with the next elections from EuropeElects

@author Miguel C. Matos
"""
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def download_page(uri: str) -> BeautifulSoup:
    """Download the page and cast it to a BeautifulSoup object"""
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    }

    payload = ""

    response = requests.request("GET", uri, data=payload, headers=headersList)

    return BeautifulSoup(response.text, "html.parser")


def parse_page(b: BeautifulSoup) -> list[dict]:
    """Parse the page into a dictionary with the elections information"""
    year = b.find_all("td", {"colspan": 3})[1].text

    table = b.find("table")
    rows = table.find_all("tr")  # type:ignore

    # Initialize the result dictionary
    result = list()

    # Iterate through the rows
    for row in rows:
        # Find the country, election type, and date cells
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        # Extract the country, election type, and date from the cells
        country = cells[0].text.encode("utf8").decode("utf8")
        election_type = cells[1].text
        date_str = cells[2].text + f" {year}"
        # parse date to machine readable
        try:
            date = datetime.strptime(date_str, "%d %B %Y")
        except Exception:
            continue

        # Add the country, election type, and date to the result dictionary
        result.append(
            {"country": country, "election_type": election_type, "date": date}
        )

    return result


def generate_ics_file(elections: list[dict]):
    """Generate an ICS file with the election dates"""
    file_str = (
        "BEGIN:VCALENDAR\n"
        + "PRODID:-//BobChat//European Elections v1.0//EN\n"
        + "VERSION:2.0\n"
        + "CALSCALE:GREGORIAN\n"
        + "METHOD:PUBLISH\n"
        + "X-WR-CALNAME:Eleições na Europa\n"
        + "X-WR-TIMEZONE:UTC\n"
        + "X-WR-CALNAME:Eleições na Europa\n"
    )

    for elec in elections:
        begin_date: datetime = elec["date"]
        # one day later
        end_date: datetime = begin_date + timedelta(days=1)
        file_str += (
            "BEGIN:VEVENT\n"
            + f"DTSTART;VALUE=DATE:{begin_date.strftime('%Y%m%d')}\n"
            + f"DTEND;VALUE=DATE:{end_date.strftime('%Y%m%d')}\n"
            + "CLASS:PUBLIC\n"
            + f"DESCRIPTION:{elec['election_type']}\n"
            + f"SUMMARY:{elec['country']} Elections 🗳️\n"
            + "TRANSP:TRASPARENT\n"
            + "END:VEVENT\n"
        )

    file_str += "END:VCALENDAR"

    with open("elections.ics", "w") as f:
        f.write(file_str)


def main():
    uri = "https://europeelects.eu/calendar"
    for _ in range(5):
        try:
            b = download_page(uri)
            break
        except:
            continue
    else:
        print("Could not download the page")
        return
    res = parse_page(b)
    generate_ics_file(res)


if __name__ == "__main__":
    main()
