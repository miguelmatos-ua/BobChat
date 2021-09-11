import os
import sys
import requests
from urllib.parse import urlparse
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]


def get_last_tweet_id():
    """Get the last tweet id

    Reads from the ``last.txt`` file, the id of the last sent tweet.

    Returns:
        (str): Id of the last sent tweet

    """
    with open("last.txt") as last_time_tweet:
        last = last_time_tweet.readlines()[-1]

    return last


def get_user_tweets(since_id, user=21390437):
    """Get user Tweets

    Returns the 100 most recent tweets of a specific user.

    Args:
        since_id (str): Id of the last sent tweet
        user (int, optional): Id of the user. Defaults to 21390437 (@SLBenfica account).

    Returns:
        (list, None): Most recent tweets
    """
    uri = f"https://api.twitter.com/2/users/{user}/tweets?max_results=100&since_id={since_id}"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }

    with requests.get(uri, headers=headers) as r:
        j: dict = r.json()

    return j.get("data")


def check_eleven_is_out(tweets):
    for tweet in tweets:
        if "JÁ HÁ ONZE" in tweet["text"]:
            return tweet["id"]

    return None


def send_tweet_message(tweet):
    tweet_uri = f"https://twitter.com/SLBenfica/status/{tweet}"
    telegram_uri = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={tweet_uri}"
    return requests.get(urlparse(telegram_uri).geturl())


if __name__ == "__main__":
    last = get_last_tweet_id()
    user_tweets = get_user_tweets(last)
    if not user_tweets:
        print("There are no user tweets")
        sys.exit(1)

    lineup_tweet = check_eleven_is_out(user_tweets)

    if not lineup_tweet:
        print("There is not lineup tweet")
        sys.exit(0)

    # add tweet to last.txt file
    with open("last.txt", "w") as last:
        last.write(lineup_tweet)

    print(send_tweet_message(lineup_tweet))
