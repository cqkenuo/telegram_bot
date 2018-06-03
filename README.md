# telegram_bot

This is a personalized telegram bot with the following commands available to users: 

- /scan: Performs a port scan on the specified address passed as a parameter i.e. /scan <ip address>
- /monitor: Sniffs the packets on the host machine running the script. Packet count to return is an optional parameter i.e. /monitor <number>
- /arp: Performs a network scan for all the devices connected to the script hosts network
- /prev: Calls the previously received command
- /trace: Runs a traceroute to the specified website/address (admin-only)
- /reg: Registers the user as an admin only if a valid key is passed as a parameter
- /help: Returns a list of available commands with descriptions
- /img: Returns a random image result from the search (safe search is off by default)
- /r34: Performs an r34 search for the provided search term
- /clear: Clears any cache arrays present (admin-only)
- /log: Returns the debugging log file (admin-only - personal information still saved in this version of the bot)
- /live: Returns a random result from the specified live leak search
- /mybb: Returns the specified number (default 5) of the latest articles from the MyBroadband website
- /b: Pulls a random image from 4chan.org/b (use at own peril)
- /dns: Performs a DNS lookup on the provided hostname
- /logs: Returns the backed-up log files (admin-only)
- /clear_logs: Deletes the backed up log files (admin-only)

## Example usage (commandline): 

#### Requirements
##### Note: As this bot uses the PyX package to create pdf dumps, a form of the LaTeX software package needs to be installed
- The LaTeX packages can be found at [LaTeX](https://www.latex-project.org/get/#tex-distributions)
- An already set-up instance of MySQL needs to be running for this bot to work

#### Steps
1. Modify the `template_config.json` to suit your setup and rename to `config.json`

2. Install the required packages: `pip install -r requirements.txt --upgrade`

3. Run the following in console / terminal: `python test_bot.py`

4. Then in telegram open the chat link: [telegram_bot](t.me/thotman_test_bot)

## Example usage in code
```python
from telegram_bot import run


if __name__ == "__main__":
    run()

```