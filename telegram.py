import os

import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
MESSAGE = os.environ.get("MESSAGE", "")


def main():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": MESSAGE})
    if resp.status_code != 200:
        raise Exception(f"Error sending telegram message: {resp.text}")


if __name__ == "__main__":
    main()
