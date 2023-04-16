from time import perf_counter_ns
import os
import telegram
from functools import wraps

# load environmental variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("The value of BOT_TOKEN is not defined")
CHAT_ID = os.environ.get("CHAT_ID")
if not CHAT_ID:
    raise ValueError("The value of the CHAT_ID is not defined")

bot = telegram.Bot(BOT_TOKEN)


def send_telegram(func):
    """Send return value to Telegram channel"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return_vals = func(*args, **kwargs)
        bot.send_message(chat_id=CHAT_ID, text=return_vals)

    return wrapper


def time_it(func):
    """Print the execution time after the execution of the function"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = perf_counter_ns()
        return_vals = func(*args, **kwargs)
        t2 = perf_counter_ns()

        print(" Execution Time: {} s".format(t2 - t1))
        return return_vals

    return wrapper
