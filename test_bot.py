import telepot
from telepot.loop import MessageLoop
import json
import sys
import time
from bot import Bot, messages, bot_commands
from log import log, LOG_FILE
import threading


CONFIG_FILE = "config.json"
config = json.load(open(CONFIG_FILE, "r"))

bot = telepot.Bot(config["token"])
b = Bot(bot)


def handle_messages(msg):
    global b

    if msg['text'] == str("/terminate " + config["terminate_val"]):
        os.kill(os.getpid(), 0)

    if not b.running:

        log("handle_messages()", "Starting bot")

        if msg['text'] == "/start":
            b = Bot(bot)
            b.start()

        content_type, chat_type, chat_id = telepot.glance(msg)
        bot.sendMessage(chat_id, "Bot starting up...")

    else:
        messages.append(msg)


if __name__ == "__main__":
    import os

    try:
        os.remove(LOG_FILE)
    except (OSError, FileNotFoundError):
        pass

    log("main()", "Starting message loop")

    b.start()

    MessageLoop(bot, handle_messages).run_as_thread()

    while True:
        time.sleep(0.2)
