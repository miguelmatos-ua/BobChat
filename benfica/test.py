import os

def vars_in_path():
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CHAT_ID = os.environ.get("CHAT_ID")

    assert BOT_TOKEN and CHAT_ID

if __name__ == "__main__":
    vars_in_path()