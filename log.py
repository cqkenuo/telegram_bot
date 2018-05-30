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


def write_to_file(file, text):
    f = open(file, 'w')
    f.write(text)
    f.close()
