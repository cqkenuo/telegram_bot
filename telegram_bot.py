import time

import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.loop import MessageLoop

from bot import Bot, clear_cache, articles_comparison
from log import log, config, clear_logs, logging, LOG_FILE

bot = telepot.DelegatorBot(config["token"], [
    pave_event_space()(
        per_chat_id(), create_open, Bot, timeout=10),
])


class SignalProcess:
    kill_now = False

    def __init__(self):
        import signal

        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        self.kill_now = True


def run(sleep_time=0.5):
    clear_logs()

    logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

    log("run()", "Starting message loop")

    start_time = time.time()
    MessageLoop(bot).run_as_thread()
    sig = SignalProcess()

    running = True
    while running:
        if sig.kill_now:
            import os
            log("run()", "SIGTERM or kill called on process. Exiting now...")
            running = False
            os.kill(os.getpid(), 0)

        if (time.time() - start_time >= 3600) and (not articles_comparison()):
            log("run()", "Clearing cache (hourly)")
            start_time = time.time()
            clear_cache()

        time.sleep(sleep_time)

