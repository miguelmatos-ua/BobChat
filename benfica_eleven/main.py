import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]


def get_user_tweets(user=21390437):
    """Get user Tweets

    Returns the 100 most recent tweets of a specific user.

    Args:
        user (int, optional): Id of the user. Defaults to 21390437.

    Returns:
        dict, None: Most recent tweets
    """
    uri = f"https://api.twitter.com/2/users/{user}/tweets"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }

    with requests.get(uri, headers=headers) as r:
        j: dict = r.json()

    return j.get("data")


def check_eleven_is_out(tweets):
    ...


def send_tweet_message(tweet):
    ...


if __name__ == "__main__":
    ...
