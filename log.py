import json

CONFIG_FILE = "config.json"
config = json.load(open(CONFIG_FILE, "r"))

# Log file directory
LOG_FILE = config["log_file"]
WRITE_TO_LOG = config['write_to_log_file']


def log(origin, message):
    if message:
        if WRITE_TO_LOG:
            f = open(LOG_FILE, "a")
            f.write("[" + origin + "] " + str(message) + "\n")
            f.close()

        print("[" + origin + "] " + str(message))


def clear_logs():
    import os

    try:
        os.remove(LOG_FILE)
    except (OSError, FileNotFoundError):
        pass


def write_to_file(file, text):
    f = open(file, 'w')
    f.write(text)
    f.close()
