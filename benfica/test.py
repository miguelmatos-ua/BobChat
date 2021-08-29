import unittest
from unittest.mock import MagicMock
from main import Benfica
from datetime import datetime


MOCKED_RESPONSE = """
{
  "count": 1,
  "filters": {
    "dateFrom": "2021-08-21",
    "dateTo": "2021-08-22",
    "permission": "TIER_ONE",
    "limit": 100
  },
  "matches": [
    {
      "id": 333001,
      "competition": {
        "id": 2017,
        "name": "Primeira Liga",
        "area": {
          "name": "Portugal",
          "code": "PRT",
          "ensignUrl": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Flag_of_Portugal.svg"
        }
      },
      "season": {
        "id": 755,
        "startDate": "2021-08-08",
        "endDate": "2022-05-15",
        "currentMatchday": 3,
        "winner": null
      },
      "utcDate": "2021-08-21T17:00:00Z",
      "status": "SCHEDULED",
      "matchday": 3,
      "stage": "REGULAR_SEASON",
      "group": null,
      "lastUpdated": "2021-08-08T08:20:09Z",
      "odds": {
        "msg": "Activate Odds-Package in User-Panel to retrieve odds."
      },
      "score": {
        "winner": null,
        "duration": "REGULAR",
        "fullTime": {
          "homeTeam": null,
          "awayTeam": null
        },
        "halfTime": {
          "homeTeam": null,
          "awayTeam": null
        },
        "extraTime": {
          "homeTeam": null,
          "awayTeam": null
        },
        "penalties": {
          "homeTeam": null,
          "awayTeam": null
        }
      },
      "homeTeam": {
        "id": 5533,
        "name": "Gil Vicente FC"
      },
      "awayTeam": {
        "id": 1903,
        "name": "Sport Lisboa e Benfica"
      },
      "referees": []
    }
  ]
""".lower().replace(" ", "") .replace("\n", "").replace("\t", "") # remove whitespaces and lower

MOCKED_RESPONSE_NO_GAME = """
{
  "count": 0,
  "filters": {
    "dateFrom": "2021-08-22",
    "dateTo": "2021-08-23",
    "permission": "TIER_ONE",
    "limit": 100
  },
  "matches": []
}""".lower().replace(" ", "").replace("\n", "").replace("\t", "")  # remove whitespaces and lower


class TestBenficaMethods(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.benficaMock = Benfica()

    def test_get_token(self):
        """Get football api and telegram token"""
        self.assertIsNotNone(Benfica.get_api_token(), "$FOOTBALL_API variable must be defined in the environment")

    def test_when_game_today(self):
        self.benficaMock.today = MagicMock("2021-08-21")  # return 21/ago when method called
        self.assertEqual(self.benficaMock.today.return_value, "2021-08-21", "Mock is not working")
        response = self.benficaMock.get_today_game().lower().replace(" ", "").replace("\n", "").replace("\t", "")

        self.assertEqual(response, MOCKED_RESPONSE, "The supposed response is not the correct one")

    def test_when_not_game_today(self):
        self.benficaMock.today = MagicMock("2021-08-22")

        response = self.benficaMock.get_today_game().lower().replace(" ", "").replace("\n", "").replace("\t", "")

        self.assertEqual(response, MOCKED_RESPONSE_NO_GAME, "The supposed response is not the correct one")


if __name__ == '__main__':
    unittest.main()
