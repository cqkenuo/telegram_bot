import time

import telepot
from telepot.loop import MessageLoop

from bot import Bot, messages, articles_comparison
from log import log, config, clear_logs

bot = telepot.Bot(config["token"])
b = Bot(bot)


class SignalProcess:
    kill_now = False

    def __init__(self):
        import signal

        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        self.kill_now = True


def run(sleep_time=0.2):
    clear_logs()

    log("run()", "Starting message loop")
    b.start()

    start_time = time.time()

    MessageLoop(bot, handle_messages).run_as_thread()
    sig = SignalProcess()

    while True:
        if sig.kill_now:
            import os
            log("run()", "SIGTERM or kill called on process. Exiting now...")
            os.kill(os.getpid(), 0)

        if (time.time() - start_time >= 3600) and (not articles_comparison()):
            log("run()", "Clearing cache on the hour")
            start_time = time.time()
            b.clear_cache(None)

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
