from random import randint

import nmap
import telepot
from threading import Thread

from commands import bot_commands, command_descriptions, restricted_commands
from database import RegisterDB
from log import log, LOG_FILE, LOG_BACKUPS
from web_scraping import search, r34, live_leak, my_bb, chan
from util import get_pc_stats

default_port_range = '22-5000'

messages = []
packets = []
spammers = []
prev_commands = {}

# Image cache
searches = []
results = {}

# MyBroadband cache
articles = []

PACKETS_FILE = 'packets'
TRACE_ROUTE_FILE = 'traceroute'
MAX_MESSAGE_LENGTH = 4095
MAX_MESSAGE_LENGTH_OFFSET = MAX_MESSAGE_LENGTH - 150


def clear_cache():
    searches.clear()
    results.clear()
    spammers.clear()
    packets.clear()
    prev_commands.clear()
    articles.clear()


# Caches the MyBroadband articles
def load_articles():
    global articles
    articles = my_bb()


class Bot(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(Bot, self).__init__(*args, **kwargs)

        self.running = True
        self.db = RegisterDB()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        command = str(msg['text']).split(" ")[0].lower()

        try:
            if command == "/clear_logs" and chat_id in spammers:
                self.sender.sendMessage("Please stop spamming")
                return
            elif command in bot_commands:
                Thread(target=self.parse_command, args=(msg['text'], chat_id,)).start()
                # self.parse_command(msg['text'], chat_id)
            elif content_type == 'text' and msg['text']:
                # self.bot.sendMessage(chat_id, msg['text'])
                if chat_id not in spammers:
                    spammers.append(chat_id)
                else:
                    self.sender.sendMessage("Please stop spamming")
        except:
            log('Bot.handle_message()', 'Unspecified exception caught', True)
            pass

    def parse_command(self, cmd, chatid):
        msg = ''
        try:
            cmd = str(cmd).lower()
            try:
                split_arr = cmd.split(" ")

                for s in split_arr:
                    # log("Bot.parse_command()", "s: " + str(s))

                    if s != split_arr[0]:
                        msg += s + " "

                msg = msg.strip()
                cmd = split_arr[0]
            except IndexError:
                pass

            if not cmd:
                return

            if str(cmd).split(" ")[0] in bot_commands:
                log("Bot.parse_command()", "command received: " + cmd)

                # /scan
                if cmd == bot_commands[0].lower():
                    self.scan(msg)

                # /prev
                elif cmd == bot_commands[3].lower():
                    if prev_commands:
                        self.parse_command(prev_commands[chatid], chatid)
                    return

                # /reg
                elif cmd == bot_commands[5].lower():
                    # add to spammers
                    if chatid not in spammers:
                        spammers.append(chatid)

                    if not self.db.user_exists(chatid) and not self.db.clashes(chatid, msg):
                        self.register(chatid, msg)
                    else:
                        self.sender.sendMessage("You are already registered or the key provided has already been used.")

                # /help
                elif cmd == bot_commands[6].lower():
                    self.print_help()

                # /img
                elif cmd == bot_commands[7].lower():
                    self.search(msg)

                # /r34
                elif cmd == bot_commands[8].lower():
                    self.r34(msg)

                # /live
                elif cmd == bot_commands[11].lower():
                    self.live(msg)

                # /mybb
                elif cmd == bot_commands[12].lower():
                    self.my_broadband(msg)

                # /b
                elif cmd == bot_commands[13].lower():
                    self.chanb()

                # /dns
                elif cmd == bot_commands[14].lower():
                    self.dns(msg)

                # Admin-only commands
                elif self.db.user_exists(chatid):

                    # # /monitor
                    # if cmd == bot_commands[1].lower():
                    #     self.sender.sendMessage("Starting wifi monitor on local network")
                    #     threading.Thread(target=self.sniff_packets(msg)).start()

                    # /arp
                    if cmd == bot_commands[2].lower():
                        self.arp(msg)

                    # /trace
                    # elif cmd == bot_commands[4].lower():
                    #     self.trace(msg)

                    # /clear
                    elif cmd == bot_commands[9].lower():
                        self.clear_cache()

                    # /log
                    elif cmd == bot_commands[10].lower():
                        try:
                            f = open(LOG_FILE, 'r')
                            self.sender.sendDocument(f)
                        except:
                            self.sender.sendMessage("Log file could not be opened...")
                            pass

                    # /logs
                    elif cmd == bot_commands[15].lower():
                        self.send_logs()

                    # /logs
                    elif cmd == bot_commands[16].lower():
                        self.clear_logs()

                    # /stats
                    elif cmd == bot_commands[17].lower():
                        self.stats()

                elif cmd in restricted_commands:
                    self.sender.sendMessage('Insufficient privileges to run this command')

                else:
                    self.sender.sendMessage("Invalid command")

            prev_commands[chatid] = str(cmd + " " + msg)

        except:
            log("parse_command()", "Unspecified exception caught", True)
            self.sender.sendMessage("Unspecified exception occurred")
            pass

    def scan(self, msg):
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

        message = ''

        self.sender.sendMessage("Starting nmap scan: \nhost: " + msg
                                + "\nports: " + ports)

        nm = nmap.PortScanner()  # instantiate nmap.PortScanner object
        nm.scan(msg, ports)  # scan host 127.0.0.1, ports from 22 to 443

        # log("Bot.scan()", "hosts: " + str(nm.all_hosts()))

        for host in nm.all_hosts():

            message += '\n\n----------------------------------------------------\n'
            message += 'Host : %12s (%s)' % (host, nm[host].hostname()) + '\n'
            message += 'State : %12s' % nm[host].state() + '\n'

            for proto in nm[host].all_protocols():
                message += '----------\n'
                message += 'Protocol : {}\n'.format(proto)

                col_width = max(len(str(nm[host][proto][row]['name'])) for row in nm[host][proto].keys()) + 4  # padding

                message += '\n{} \t {} \t\t {}\n'.format('Port: '.ljust(col_width), 'State: '.ljust(col_width),
                                                         'Name: '.ljust(col_width))
                message += '====================================\n'

                for port in nm[host][proto].keys():
                    p = nm[host][proto][port]
                    message += '{} \t {} \t\t {}\n'.format(str(port).ljust(col_width), str(p['state']).ljust(col_width),
                                                           str(p['name']).ljust(col_width))

        if not message:
            message = "No results returned..."

        self.sender.sendMessage(str(message + "\n"))

    def arp(self, msg):
        self.sender.sendMessage("Starting nmap scan on: " + str(msg) + "/24")

        nm = nmap.PortScanner()  # instantiate nmap.PortScanner object
        nm.scan(hosts=str(str(msg) + "/24"), arguments='-sP')  # ( -PE -PA21,23,80,135,3389,27036)   scan host

        hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

        col_width = max(len(str(row)) for row in hosts_list) + 4  # padding

        message = "{} {} {}".format("Host".ljust(col_width), "Status".ljust(col_width), 'Host'.ljust(col_width))
        message += "\n=======================================\n"

        for host, status in hosts_list:
            message += str('{} {} {}\n'.format(str(host + ':').ljust(col_width), str(status).ljust(col_width),
                                               str(nm[host].hostname()).ljust(col_width)))

        if not message:
            message = "No results returned..."

        if len(message) >= MAX_MESSAGE_LENGTH:
            mess = []

            while len(message) >= MAX_MESSAGE_LENGTH:
                end_point = message.find('\n', MAX_MESSAGE_LENGTH_OFFSET)
                mess.append(message[0:end_point])
                message = message[end_point + 1:]  # remove first 4k bytes

            if message:
                mess.append(message)

            for i in mess:
                self.sender.sendMessage(i)

        else:
            self.sender.sendMessage(str(message))

    # def trace(self, msg):
    #     from scapy.layers.inet import traceroute
    #
    #     self.sender.sendMessage("Starting traceroute to: " + msg)
    #
    #     try:
    #         # log("Bot.trace()", "msg: \"" + msg + "\"")
    #         res, unans = traceroute([str(msg)], dport=[80, 443], maxttl=20, retry=-2)
    #
    #         res.pdfdump(TRACE_ROUTE_FILE)
    #         f = open(str('./' + TRACE_ROUTE_FILE + '.pdf'), 'rb')
    #
    #         self.sender.sendDocument(f)
    #     except:
    #         log("Bot.trace()", "Unspecified error", True)
    #         raise

    # def sniff_packets(self, msg):
    #     try:
    #         os.remove(str('./' + PACKETS_FILE + '.pdf'))
    #     except (OSError, FileNotFoundError):
    #         pass
    #
    #     msg = str(msg).lower()
    #     target = ''
    #     try:
    #         split_arr = msg.split(" ")
    #         msg = split_arr[0]
    #         target = split_arr[1]
    #     except IndexError:
    #         pass
    #
    #     count = 5
    #     if msg and str(msg).isnumeric():
    #         count = int(msg)
    #
    #     filter_str = 'icmp and host {}'.format(target)  # 'ip 137.215.98.24'
    #     if is_windows():
    #         res = sniff(filter=filter_str, count=count)
    #     else:
    #         res = sniff(iface='wlx7c8bca1c000a', filter=filter_str, count=count)
    #
    #     # res.pdfdump(PACKETS_FILE)
    #     #
    #     # f = open(str('./' + PACKETS_FILE + '.pdf'), 'rb')
    #     # if f:
    #     #     self.sender.sendDocument(f)
    #     # else:
    #     #     self.sender.sendMessage('No results returned...')

    def register(self, chatid, msg):
        log("Bot.register()", "Confirming whether user is registered")

        self.sender.sendMessage("Confirming your identity...")

        if self.db.exists(msg) and not self.db.clashes(chatid, msg):
            log("Bot.register()", "Registering new user")
            self.db.insert(chatid, msg)

            self.sender.sendMessage("You are now registered as an admin")
        else:
            self.sender.sendMessage("Could not register you. Invalid parameters provided")

    def print_help(self):

        ret = 'Currently supported commands: \n\n'

        for x in range(0, len(command_descriptions)):
            ret += str(bot_commands[x]) + ':\t' + str(command_descriptions[x]) + '\n\n'

        self.sender.sendMessage(ret)

    def search(self, msg):
        if msg not in searches:
            images = search(msg)
            results[msg] = images
            searches.append(msg)
        else:
            images = results[msg]

        if len(images) < 1:
            self.sender.sendMessage("No results returned...")
        else:
            self.sender.sendPhoto(images[randint(0, len(images) - 1)])

    def r34(self, msg):
        images = r34(msg)

        if len(images) < 1:
            self.sender.sendMessage("No results returned...")
        else:
            url = images[randint(0, len(images) - 1)]
            self.sender.sendPhoto(url)

    def live(self, msg):
        res = live_leak(msg)

        if len(res) < 1:
            self.sender.sendMessage("No results returned...")
        else:
            url = res[randint(0, len(res) - 1)]
            self.sender.sendMessage(url)

    def my_broadband(self, msg):
        global articles

        if len(articles) < 1:
            articles = my_bb()

        if len(articles) < 1:
            self.sender.sendMessage("No results returned...")
        else:
            count = 5
            if msg:
                count = int(msg)

            for x in range(0, count):
                self.sender.sendMessage(articles[x])

    def chanb(self):
        res = chan()

        if len(res) < 1:
            self.sender.sendMessage("No results returned...")
        else:
            url = res[randint(0, len(res) - 1)]
            # log('Bot.r34()', 'using: ' + url)
            self.sender.sendPhoto(url)

    def clear_cache(self):
        searches.clear()
        results.clear()
        spammers.clear()
        packets.clear()
        prev_commands.clear()
        articles.clear()

        self.sender.sendMessage("Local cache cleared")

    # Should return the IP Address(es) of the specified host
    # Using dns-python when socket.hostname() should suffice
    def dns(self, msg):
        from dns import resolver

        res = resolver.Resolver()
        res.nameservers = ['8.8.8.8', '8.8.4.4']

        try:
            myAnswers = resolver.query(str(msg), 'A')

            message = ''.encode('utf-8')
            if myAnswers:
                for rdata in myAnswers:
                    message += str(str(rdata) + '\n').encode('utf-8')

                self.sender.sendMessage(message.decode('utf-8'))
            else:
                self.sender.sendMessage('No results returned...')

        except:
            log('Bot.dns', 'Unspecified error', True)
            self.sender.sendMessage('Query failed')
            pass

    def send_logs(self):
        from os import walk, path
        from zipfile import ZipFile

        found = False

        for (dirpath, dirnames, filenames) in walk(LOG_BACKUPS):

            with ZipFile('logs.zip', 'w') as myzip:
                for filename in filenames:
                    if filename.endswith('.log'):
                        found = True
                        myzip.write(path.join(dirpath, filename))

                # append the current log file to the zip file
                myzip.write(LOG_FILE)

                myzip.close()

        if found:
            f = open('./logs.zip', 'rb')
            self.sender.sendDocument(f)
            f.close()
        else:
            self.sender.sendMessage('No backed-up log files found')

    def clear_logs(self):
        from shutil import rmtree
        rmtree(LOG_BACKUPS)

        self.sender.sendMessage('Backed-up log files deleted')

    def stats(self):
        msg = get_pc_stats()

        self.sender.sendMessage(msg)
