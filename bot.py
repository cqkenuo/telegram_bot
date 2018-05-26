import threading
import telepot
from scapy.all import *
from log import log
import json
import nmap
from database import RegisterDB, is_windows

bot_commands = ["/start", "/stop", "/scan", "/monitor", "/arp", "/prev", "/trace",
                "/reg"]

monitor_cmd_call = "python wifi-monitor.py -j"
default_port_range = '22-50000'

messages = []
packets = []
spammers = []
prev_commands = {}

CONFIG_FILE = "config.json"
PACKETS_FILE = "packets"
config = json.load(open(CONFIG_FILE, "r"))


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
                print("handling message: " + str(m))
                messages.remove(m)

            time.sleep(0.5)

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

        log("Bot.handle_message()", telepot.glance(msg, flavor=flavor))

        if str(msg['text']).split(" ")[0] in bot_commands:
            threading.Thread(target=self.parse_command(msg['text'], chat_id)).start()
        elif content_type == 'text' and msg['text']:
            # self.bot.sendMessage(chat_id, msg['text'])
            if chat_id not in spammers:
                spammers.append(chat_id)
            else:
                self.bot.sendMessage(chat_id, "Please stop spamming")

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
                    print(msg)
                    if msg and msg == str(config["terminate_val"]).lower():
                        self.running = False
                        self.bot.sendMessage(chatid, "Bot stopping...")
                    else:
                        self.bot.sendMessage(chatid, "Invalid command")

                # /scan
                elif cmd == bot_commands[2].lower():
                    self.scan(msg, chatid)

                # /monitor
                elif cmd == bot_commands[3].lower():
                    # output = subprocess.check_output(monitor_cmd_call, shell=True)
                    # self.bot.sendMessage(chatid, output)

                    self.bot.sendMessage(chatid, "Starting wifi monitor on local network")

                    threading.Thread(target=self.sniff_packets(chatid, msg)).start()

                # /arp
                elif cmd == bot_commands[4].lower():
                    self.arp(msg, chatid)

                # /prev
                elif cmd == bot_commands[5].lower():
                    if prev_commands:
                        self.parse_command(prev_commands[chatid], chatid)
                    return

                elif cmd == bot_commands[6].lower():
                    self.trace(msg, chatid)

                elif cmd == bot_commands[7].lower():
                    if msg == config['']:
                        self.register(chatid)

                else:
                    self.bot.sendMessage(chatid, "Invalid command")

            prev_commands[chatid] = str(cmd + " " + msg)

        except:
            log("parse_command()", "Unspecified exception caught")
            self.bot.sendMessage(chatid, "Unspecified exception occurred")
            raise

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
        # from scapy.layers.l2 import Ether
        #
        # self.bot.sendMessage(chatid, "Starting arp scan on local network")
        #
        # from scapy.layers.l2 import ARP
        # ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(msg + "/24")), timeout=2)
        #
        # devices = []
        #
        # for a in ans.res:
        #     pos1 = [m.start() for m in re.finditer('pdst', str(a))]
        #     pos2 = [m.start() for m in re.finditer('psrc', str(a))]
        #
        #     for pos in pos1:
        #         val = str(a)[pos + 5:str(a).find(' ', pos)]
        #         if val not in devices:
        #             devices.append(val)
        #
        #     for pos in pos2:
        #         val = str(a)[pos + 5:str(a).find(' ', pos)]
        #         if val not in devices:
        #             devices.append(val)
        #
        # final_str = ""
        # for d in devices:
        #     final_str += str(d) + "\n"  # + " hostname: " + "\n"
        #
        # if not final_str:
        #     final_str = "No results returned..."
        #
        # self.bot.sendMessage(chatid, str(final_str))

        self.bot.sendMessage(chatid, "Starting nmap scan on: " + str(msg) + "/24")

        nm = nmap.PortScanner()  # instantiate nmap.PortScanner object
        nm.scan(hosts=str(str(msg) + "/24"), arguments='-sP')  # ( -PE -PA21,23,80,135,3389,27036)   scan host

        # log("Bot.scan()", "hosts: " + str(nm.all_hosts()))

        hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

        col_width = max(len(str(row)) for row in hosts_list) + 4  # padding
        print("col_width: " + str(col_width))
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
            log("Bot.trace()", "jews 1")
            res.graph(target="> ./graph.svg")
            log("Bot.trace()", "jews 2")

            time.sleep(5)

            with open("./graph.svg") as f:
                m = f.readlines()

            log("Bot.trace()", "jews 3 + " + str(m))
        except:
            log("Bot.trace()", "Unspecified error")
            raise

        if not m:
            m = "No results returned "

        self.bot.sendMessage(chatid, m)

    def sniff_packets(self, chatid, msg):
        # while self.running:
        # pc = pcap.pcap()  # construct pcap object
        # pc.setfilter('icmp')  # filter out unwanted packets
        # for timestamp, packet in pc:
        #     self.bot.sendMessage(dpkt.ethernet.Ethernet(packet), chatid)

        try:
            os.remove(str('./' + PACKETS_FILE + '.pdf'))
        except (OSError, FileNotFoundError):
            pass

        if not msg or not str(msg).isnumeric():
            msg = 5

        filter_str = 'ip 137.215.98.24'  # "icmp and host"
        if is_windows():
            res = sniff(filter=filter_str, count=int(msg))
        else:
            res = sniff(iface='wlx7c8bca1c000a', filter=filter_str, count=int(msg))

        res.pdfdump(PACKETS_FILE)

        f = open(str('./' + PACKETS_FILE + '.pdf'), 'rb')

        self.bot.sendDocument(chatid, f)

        time.sleep(0.25)

    def register(self, chatid, msg):
        log("Bot.register", "Confirming whether user: " + str(chatid)
            + " is registered")

        self.bot.sendMessage(chatid, "Confirming your identity...")

        if self.db.exists(msg):
            self.db.insert(chatid, msg)
