import time

import telepot
from telepot.delegate import pave_event_space, per_chat_id, create_open
from telepot.loop import MessageLoop

from bot import Bot, clear_cache, load_articles
from log import log, config, clear_logs, logging, LOG_FILE

# Interval at which cache is cleared
CACHE_CLEAR_PERIOD = config['cache_clear_interval']
DEBUGGING = config['debugging']

# Delegator bot for multiple threaded instances of the Bot class
bot = telepot.DelegatorBot(config["token"], [
    pave_event_space()(
        per_chat_id(), create_open, Bot, timeout=10),
])


# Used to catch SIGINT and SIGTERM signals
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

    if not DEBUGGING:
        load_articles()

    running = True
    while running:
        if sig.kill_now:
            import os
            log("run()", "SIGTERM or kill called on process. Exiting now...")
            running = False
            os.kill(os.getpid(), 0)

        if (time.time() - start_time) >= CACHE_CLEAR_PERIOD:
            log("run()", "Clearing cache and resetting log file (every {} hour(s)".format(CACHE_CLEAR_PERIOD/3600))
            start_time = time.time()

            # reset cache
            clear_cache()

            # Reload articles
            load_articles()

            # Reset log file and copy the previous one to the backup directory
            # Keeps log files from becoming too big
            clear_logs()

        time.sleep(sleep_time)

