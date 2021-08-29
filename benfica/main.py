import requests
import os
from datetime import datetime


class Benfica:
    today = datetime.today().strftime("%Y-%m-%m")

    @staticmethod
    def get_api_token():
        return os.environ.get("FOOTBALL_API")

    def get_today_game(self) -> str:
        # assert self.today == "2021-08-21"
        return "Hello"


if __name__ == "__main__":
    ...