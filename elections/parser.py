"""
Generate a file with the next elections from EuropeElects

@author Miguel C. Matos
"""
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict


def download_page(uri: str) -> BeautifulSoup:
    """Download the page and cast it to a BeautifulSoup object"""
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
    }

    payload = ""

    response = requests.request("GET", uri, data=payload, headers=headersList)

    return BeautifulSoup(response.text, "html.parser")


def parse_page(b: BeautifulSoup) -> dict:
    """Parse the page into a dictionary with the elections information"""
    year = b.find_all("td", {"colspan": 3})[1].text

    table = b.find("table")
    rows = table.find_all("tr")  # type:ignore

    # Initialize the result dictionary
    result = defaultdict(list)

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
            formatted_date = date.strftime("%Y-%m-%d")
        except Exception:
            continue

        # Add the country, election type, and date to the result dictionary
        result[country].append({"election_type": election_type, "date": formatted_date})

    return result


def generate_ics_file():
    """Generate an ICS file with the election dates"""
    ...


def main():
    uri = "https://europeelects.eu/calendar"
    b = download_page(uri)
    res = parse_page(b)
    __import__("pprint").pprint(res)


if __name__ == "__main__":
    main()
