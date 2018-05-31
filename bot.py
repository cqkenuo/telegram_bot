from random import randint

import nmap
import telepot
from scapy.all import *

from commands import bot_commands, command_descriptions, restricted_commands
from database import RegisterDB, is_windows
from log import log, config, LOG_FILE
from search import search, r34

monitor_cmd_call = "python wifi-monitor.py -j"
default_port_range = '22-5000'

messages = []
packets = []
spammers = []
prev_commands = {}

# Image cache
searches = []
results = {}

PACKETS_FILE = 'packets'
TRACE_ROUTE_FILE = 'traceroute'


class Bot(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)

        self.running = True
        self.bot = bot
        self.db = RegisterDB()

    def run(self):
        while self.running:
            for m in messages:
                self.handle_message(m)
                # print("handling message: " + str(m))
                messages.remove(m)

            if len(results) > 1000:
                results.clear()
                searches.clear()

            time.sleep(0.2)

        # wait for all threads to stop
        time.sleep(5)
        self.stop()

    def stop(self):
        self.running = False
        spammers.clear()
        messages.clear()
        log("Bot.stop()", "Bot stopping...")

    def handle_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        flavor = telepot.flavor(msg=msg)
        # print(content_type, chat_type, chat_id)

        # log("Bot.handle_message()", telepot.glance(msg, flavor=flavor))

        try:
            if str(msg['text']).split(" ")[0] in bot_commands:
                threading.Thread(target=self.parse_command(msg['text'], chat_id)).start()
            elif content_type == 'text' and msg['text']:
                # self.bot.sendMessage(chat_id, msg['text'])
                if chat_id not in spammers:
                    spammers.append(chat_id)
                else:
                    self.bot.sendMessage(chat_id, "Please stop spamming")
        except:
            traceback.print_exc()
            pass

    def parse_command(self, cmd, chatid):
        try:
            cmd = str(cmd).lower()
            msg = ""
            try:
                split_arr = cmd.split(" ")

                for s in split_arr:
                    # log("Bot.parse_command()", "s: " + str(s))

                    if s != split_arr[0]:
                        msg += s + " "

                msg = msg.strip()
                cmd = split_arr[0]

                # log("Bot.parse_command()", "msg: " + msg)

            except IndexError:
                pass

            if not cmd:
                return

            if str(cmd).split(" ")[0] in bot_commands:
                log("Bot.parse_command()", "command received: " + cmd)

                if cmd == bot_commands[0] and self.running:
                    self.bot.sendMessage(chatid, "Bot is already running")

                # /stop
                elif cmd == bot_commands[1].lower():
                    if (msg and msg == str(config["terminate_val"]).lower()) or (self.db.user_exists(chatid)):
                        self.running = False
                        self.bot.sendMessage(chatid, "Bot stopping...")
                    else:
                        self.bot.sendMessage(chatid, "Invalid command")

                # /scan
                elif cmd == bot_commands[2].lower():
                    self.scan(msg, chatid)

                # /prev
                elif cmd == bot_commands[5].lower():
                    if prev_commands:
                        self.parse_command(prev_commands[chatid], chatid)
                    return

                # /reg
                elif cmd == bot_commands[7].lower():
                    if not self.db.user_exists(chatid) and not self.db.clashes(chatid, msg):
                        self.register(chatid, msg)
                    else:
                        self.bot.sendMessage(chatid,
                                             "You are already registered or the key provided has already been used.")

                # /help
                elif cmd == bot_commands[8].lower():
                    self.print_help(chatid)

                # /img
                elif cmd == bot_commands[9].lower():
                    self.search(chatid, msg)

                # /r34
                elif cmd == bot_commands[10].lower():
                    self.r34(chatid, msg)

                # Admin-only commands
                elif self.db.user_exists(chatid):

                    # /monitor
                    if cmd == bot_commands[3].lower():
                        self.bot.sendMessage(chatid, "Starting wifi monitor on local network")
                        threading.Thread(target=self.sniff_packets(chatid, msg)).start()

                    # /arp
                    elif cmd == bot_commands[4].lower():
                        self.arp(msg, chatid)

                    # /trace
                    elif cmd == bot_commands[6].lower():
                        self.trace(msg, chatid)

                    # /clear
                    elif cmd == bot_commands[11].lower():
                        self.clear_cache(chatid)

                    elif cmd == bot_commands[12].lower():
                        try:
                            f = open(LOG_FILE, 'r')
                            self.bot.sendDocument(chatid, f)
                        except:
                            self.bot.sendMessage(chatid, "Log file could not be opened...")
                            pass

                elif cmd in restricted_commands:
                    self.bot.sendMessage(chatid, 'Insufficient privileges required to run this command')

                else:
                    self.bot.sendMessage(chatid, "Invalid command")

            prev_commands[chatid] = str(cmd + " " + msg)

        except:
            log("parse_command()", "Unspecified exception caught")
            self.bot.sendMessage(chatid, "Unspecified exception occurred")
            traceback.print_exc()
            pass

    def scan(self, msg, chatid):
        msg = str(msg).lower()
        port_max = ""
        try:
            split_arr = msg.split(" ")
            msg = split_arr[0]
            port_max = split_arr[1]
        except IndexError:
            pass

        ports = default_port_range
        if port_max:
            ports = port_max

        message = ""

        self.bot.sendMessage(chatid, "Starting nmap scan: \nhost: " + msg
                             + "\nports: " + ports)

        nm = nmap.PortScanner()  # instantiate nmap.PortScanner object
        nm.scan(msg, ports)  # scan host 127.0.0.1, ports from 22 to 443

        # log("Bot.scan()", "hosts: " + str(nm.all_hosts()))

        for host in nm.all_hosts():

            message += '----------------------------------------------------\n'
            message += 'Host : %12s (%s)' % (host, nm[host].hostname()) + '\n'
            message += 'State : %12s' % nm[host].state() + '\n'

            for proto in nm[host].all_protocols():
                message += '----------\n'

                message += 'Protocol : %s' % proto + "\n"

                lport = nm[host][proto].keys()
                # lport.sort()
                for port in lport:
                    p = nm[host][proto][port]
                    message += 'port: %12s \t state: %12s \t\t name: %12s' % (port, p['state'], p['name']) + "\n"

        if not message:
            message = "No results returned..."

        self.bot.sendMessage(chatid, str(message + "\n"))

    def arp(self, msg, chatid):
        self.bot.sendMessage(chatid, "Starting nmap scan on: " + str(msg) + "/24")

        nm = nmap.PortScanner()  # instantiate nmap.PortScanner object
        nm.scan(hosts=str(str(msg) + "/24"), arguments='-sP')  # ( -PE -PA21,23,80,135,3389,27036)   scan host

        # log("Bot.scan()", "hosts: " + str(nm.all_hosts()))

        hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

        col_width = max(len(str(row)) for row in hosts_list) + 4  # padding
        log('Bot.arp()', "col_width: " + str(col_width))
        message = "{:} {:}".format("Host".ljust(col_width), "Status".ljust(col_width))
        message += "\n===============================\n"

        for host, status in hosts_list:
            message += str('{:} {:}'.format(str(host + ':').ljust(col_width), str(status).ljust(col_width))) + '\n'

        if not message:
            message = "No results returned..."

        self.bot.sendMessage(chatid, str(message + "\n"))

    def trace(self, msg, chatid):
        from scapy.layers.inet import traceroute

        self.bot.sendMessage(chatid, "Starting traceroute to: " + msg)
        m = ""

        try:
            # log("Bot.trace()", "msg: \"" + msg + "\"")
            res, unans = traceroute([str(msg)], dport=[80, 443], maxttl=20, retry=-2)

            res.pdfdump(TRACE_ROUTE_FILE)
            f = open(str('./' + TRACE_ROUTE_FILE + '.pdf'), 'rb')

            self.bot.sendDocument(chatid, f)
        except:
            log("Bot.trace()", "Unspecified error")
            raise

        if not m:
            m = "No results returned "

        self.bot.sendMessage(chatid, m)

    def sniff_packets(self, chatid, msg):
        try:
            os.remove(str('./' + PACKETS_FILE + '.pdf'))
        except (OSError, FileNotFoundError):
            pass

        if not msg or not str(msg).isnumeric():
            msg = 5

        filter_str = "icmp and host"  # 'ip 137.215.98.24'
        if is_windows():
            res = sniff(filter=filter_str, count=int(msg))
        else:
            res = sniff(iface='wlx7c8bca1c000a', filter=filter_str, count=int(msg))

        res.pdfdump(PACKETS_FILE)

        f = open(str('./' + PACKETS_FILE + '.pdf'), 'rb')

        self.bot.sendDocument(chatid, f)

    def register(self, chatid, msg):
        log("Bot.register()", "Confirming whether user: " + str(chatid)
            + " is registered")

        self.bot.sendMessage(chatid, "Confirming your identity...")

        if self.db.exists(msg) and not self.db.clashes(chatid, msg):
            log("Bot.register()", "Registering new user: " + str(chatid))
            self.db.insert(chatid, msg)

            self.bot.sendMessage(chatid, "You are now registered as an admin")
        else:
            self.bot.sendMessage(chatid, "Could not register you. Invalid parameters provided")

    def print_help(self, chatid):

        ret = 'Currently supported commands: \n\n'

        for x in range(0, len(command_descriptions)):
            ret += str(bot_commands[x]) + ':\t' + str(command_descriptions[x]) + '\n\n'

        self.bot.sendMessage(chatid, ret)

    def search(self, chatid, msg):
        if msg not in searches:
            searches.append(msg)

            images = search(msg)

            results[msg] = images
        else:
            images = results[msg]

        if len(images) < 1:
            self.bot.sendMessage(chatid, "No results returned...")
        else:
            self.bot.sendPhoto(chatid, images[randint(0, len(images)-1)])

    def r34(self, chatid, msg):
        images = r34(msg)

        if len(images) < 1:
            self.bot.sendMessage(chatid, "No results returned...")
        else:
            url = images[randint(0, len(images) - 1)]
            # log('Bot.r34()', 'using: ' + url)
            self.bot.sendPhoto(chatid, url)

    def clear_cache(self, chatid):
        searches.clear()
        results.clear()
        spammers.clear()
        packets.clear()
        prev_commands.clear()

        self.bot.sendMessage(chatid, "Local cache cleared")
