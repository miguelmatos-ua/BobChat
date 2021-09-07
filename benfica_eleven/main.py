import os
import sys
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]


def get_user_tweets(user=21390437):
    """Get user Tweets

    Returns the 100 most recent tweets of a specific user.

    Args:
        user (int, optional): Id of the user. Defaults to 21390437 (@SLBenfica account).

    Returns:
        (list, None): Most recent tweets
    """
    uri = f"https://api.twitter.com/2/users/{user}/tweets?max_results=100"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }

    with requests.get(uri, headers=headers) as r:
        j: dict = r.json()

    return j.get("data")


def check_eleven_is_out(tweets):
    for tweet in tweets:
        if "JÁ HÁ ONZE" in tweet["text"]:
            return tweet["text"]

    return None


def send_tweet_message(tweet):
    telegram_uri = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}"
    return requests.get(telegram_uri.format(BOT_TOKEN, CHAT_ID, tweet["text"]))


if __name__ == "__main__":
    user_tweets = get_user_tweets()
    if not user_tweets:
        print("There are no user tweets")
        sys.exit(1)

    lineup_tweet = check_eleven_is_out(user_tweets)

    if not lineup_tweet:
        print("There is not lineup tweet")
        sys.exit(0)

    print(send_tweet_message(lineup_tweet))
