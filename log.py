import json
import logging
from datetime import datetime

CONFIG_FILE = "config.json"
config = json.load(open(CONFIG_FILE, "r"))

# Log file directory
LOG_FILE = config["log_file"]
LOG_BACKUPS = config['log_backup_dir']


def log(origin, message, is_exception=False):
    if message or is_exception:
        date = datetime.now().strftime('[%H:%M:%S - %d/%m/%Y] =>')
        message = '{} ( {} ) {}'.format(date, origin, message)

        if is_exception:
            logging.exception(message)
        else:
            logging.debug(message)

        if config['debugging']:
            print(message)


def clear_logs():
    try:
        import os
        from shutil import copyfile

        if os.path.isfile(LOG_FILE):
            if not os.path.exists(LOG_BACKUPS):
                os.makedirs(LOG_BACKUPS)

            date = datetime.now().strftime('[%H%M%S_%d-%m-%Y]')
            copyfile(LOG_FILE, '{}{}{}'.format(LOG_BACKUPS, date, str(LOG_FILE)[2:]))

            with open(LOG_FILE, 'w') as f:
                f.close()
                pass
    except (OSError, FileNotFoundError):
        log('log.py.clear_logs()', 'Could not delete log file', True)
        pass


def write_to_file(file, text):
    f = open(file, 'w')
    f.write(text)
    f.close()


def append_to_file(file, text):
    f = open(file, 'a')
    f.write(text + '\n')
    f.close()


if __name__ == "__main__":
    log('', '', True)
