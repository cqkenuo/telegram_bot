import time

import telepot
from telepot.loop import MessageLoop

from bot import Bot, messages
from log import log, config, clear_logs

bot = telepot.Bot(config["token"])
b = Bot(bot)


def run(sleep_time=0.2):
    clear_logs()

    log("main()", "Starting message loop")
    b.start()

    MessageLoop(bot, handle_messages).run_as_thread()

    while True:
        time.sleep(sleep_time)


def handle_messages(msg):
    global b

    # if msg['text'] == str("/terminate " + config["terminate_val"]):
    #     os.kill(os.getpid(), 0)

    if not b.running and msg['text'] == '/start':

        log("handle_messages()", "Starting bot")

        if msg['text'] == "/start":
            b = Bot(bot)
            b.start()

        content_type, chat_type, chat_id = telepot.glance(msg)
        bot.sendMessage(chat_id, "Bot starting up...")

    else:
        messages.append(msg)
