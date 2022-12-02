import os
import sys
import requests
from urllib.parse import urlparse

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]


def get_last_tweet_id():
    """Get the last tweet id

    Reads from the ``last.txt`` file, the id of the last sent tweet.

    Returns:
        (str): Id of the last sent tweet

    """
    with open("twitter/last.txt") as last_time_tweet:
        return last_time_tweet.readlines()[-1]


def get_user_id(user: str) -> str:
    """Get user id

    Returns the id of a specific user.

    Args:
        user (str): Username of the user

    Returns:
        (str): Id of the user

    """

    uri = f"https://api.twitter.com/2/users/by/username/{user}"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }

    with requests.get(uri, headers=headers) as r:
        j: dict = r.json()

    return j['data']['id']


def get_user_tweets(since_id: str, user: str):
    """Get user Tweets

    Returns the 100 most recent tweets of a specific user.

    Args:
        since_id (str): Id of the last sent tweet
        user (str): Id of the user.

    Returns:
        (list, None): Most recent tweets
    """
    uri = f"https://api.twitter.com/2/users/{user}/tweets?max_results=100&since_id={str(since_id).rstrip()}"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }

    with requests.get(uri, headers=headers) as r:
        j: dict = r.json()

    return j.get("data")


def check_tweet_is_out(tweets, string_filter: str):
    return [t["id"] for t in tweets if string_filter in t["text"]]


def send_tweet_message(tweet_id, twitter_username):
    tweet_uri = f"https://twitter.com/{twitter_username}/status/{tweet_id}"
    telegram_uri = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={tweet_uri}"
    return requests.get(urlparse(telegram_uri).geturl())


if __name__ == "__main__":
    username = "EuropeElects"
    tweet_filter = ""
    if len(sys.argv) > 1:
        username = sys.argv[1]
        tweet_filter = sys.argv[2] if len(sys.argv) > 2 else ""

    user_id = get_user_id(username)

    last = get_last_tweet_id()
    user_tweets = get_user_tweets(last, user_id)
    if not user_tweets:
        print("There are no user tweets")
        sys.exit(1)

    lineup_tweet = check_tweet_is_out(user_tweets, tweet_filter)

    if not lineup_tweet:
        print("There is no tweet")
        sys.exit(0)

    for tweet in lineup_tweet:
        print(send_tweet_message(tweet, username))
        # add tweet to last.txt file
        with open("twitter/last.txt", "w") as last:
            last.write(tweet)
