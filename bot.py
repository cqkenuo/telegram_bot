import telepot
from scapy.all import *
from log import log
import json

bot_commands = ["/start", "/stop", "/scan", "/monitor", "/arp"]

monitor_cmd_call = "python wifi-monitor.py -j"

messages = []
spammers = []

CONFIG_FILE = "config.json"
config = json.load(open(CONFIG_FILE, "r"))


class Bot(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)

        self.running = True
        self.bot = bot

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
                msg = cmd.split(" ")[1]
                cmd = cmd.split(" ")[0]
            except IndexError:
                pass

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
                    from scapy.layers.inet import IP
                    from scapy.layers.inet import TCP

                    self.bot.sendMessage(chatid, ("Starting port scan on: " + msg + "\nResults on the way"))

                    res, unans = sr(IP(dst=msg)
                                    / TCP(flags="S", dport=(1, 2)))

                    res = res.nsummary(lfilter=lambda s, r: (r.haslayer(TCP) and (r.getlayer(TCP).flags & 2)))

                    self.bot.sendMessage(chatid, res)

                # /monitor
                elif cmd == bot_commands[3].lower():
                    # output = subprocess.check_output(monitor_cmd_call, shell=True)
                    # self.bot.sendMessage(chatid, output)

                    self.bot.sendMessage(chatid, "Starting wifi monitor on local network")

                    threading.Thread(target=self.sniff_packets(chatid)).start()

                # /arp
                elif cmd == bot_commands[4].lower():
                    from scapy.layers.l2 import Ether

                    self.bot.sendMessage(chatid, "Starting arp scan on local network")

                    from scapy.layers.l2 import ARP
                    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(msg + "/24")), timeout=2)

                    devices = []

                    for a in ans.res:
                        pos1 = [m.start() for m in re.finditer('pdst', str(a))]
                        pos2 = [m.start() for m in re.finditer('psrc', str(a))]

                        for pos in pos1:
                            val = str(a)[pos + 5:str(a).find(' ', pos)]
                            if val not in devices:
                                devices.append(val)

                        for pos in pos2:
                            val = str(a)[pos + 5:str(a).find(' ', pos)]
                            if val not in devices:
                                devices.append(val)

                    final_str = ""
                    for d in devices:
                        final_str += str(d) + "\n"  # + " hostname: " + "\n"

                    self.bot.sendMessage(chatid, str(final_str))

                else:
                    self.bot.sendMessage(chatid, "Invalid command")

        except:
            log("parse_command()", "Unspecified exception caught")
            raise

    def sniff_packets(self, chatid):
        while self.running:
            # pc = pcap.pcap()  # construct pcap object
            # pc.setfilter('icmp')  # filter out unwanted packets
            # for timestamp, packet in pc:
            #     self.bot.sendMessage(dpkt.ethernet.Ethernet(packet), chatid)

            self.bot.sendMessage(chatid, sniff(filter="ip", prn=lambda x: x.sprintf("{IP:%IP.src% -> %IP.dst%\n}")))

            time.sleep(0.25)
