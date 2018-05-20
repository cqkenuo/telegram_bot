import telepot
from telepot.loop import MessageLoop
import json
import sys
import time
from bot import Bot, messages


CONFIG_FILE = "config.json"
config = json.load(open(CONFIG_FILE, "r"))

bot = telepot.Bot(config["token"])
b = Bot(bot)


def handle_messages(msg):
    messages.append(msg)

    global b

    if not b.running:
        if msg['text'] == "/start":
            b = Bot(bot)
            b.start()


if __name__ == "__main__":
    print("Starting message loop")

    b.start()

    MessageLoop(bot, handle_messages).run_as_thread()

    while True:
        time.sleep(1)
