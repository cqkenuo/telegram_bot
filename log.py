import json

CONFIG_FILE = "config.json"
config = json.load(open(CONFIG_FILE, "r"))

# Log file directory
LOG_FILE = config["log_file"]


def log(origin, message, debugging=True):
    if message:
        if debugging:
            f = open(LOG_FILE, "a")
            f.write("[" + origin + "] " + str(message) + "\n")
            f.close()

        print("[" + origin + "] " + str(message))
