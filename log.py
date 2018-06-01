import json
import logging
from datetime import datetime

CONFIG_FILE = "config.json"
config = json.load(open(CONFIG_FILE, "r"))

# Log file directory
LOG_FILE = config["log_file"]

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)


def log(origin, message, is_exception=False):
    if message or is_exception:
        date = datetime.now().strftime('[%H:%M:%S - %d/%m/%Y] =>')
        message = '{} ( {} ) {}'.format(date, origin, message)

        if is_exception:
            logging.exception(message)
        else:
            logging.debug(message)

        print(message)


def clear_logs():
    try:
        import os
        os.remove(LOG_FILE)
    except (OSError, FileNotFoundError):
        pass


def write_to_file(file, text):
    f = open(file, 'w')
    f.write(text)
    f.close()


if __name__ == "__main__":
    log('jew()', 'jew2')
