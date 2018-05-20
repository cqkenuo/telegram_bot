import threading
import time
import telepot


bot_commands = ["/stop"]

messages = []


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

    def handle_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        flavor = telepot.flavor(msg=msg)
        # print(content_type, chat_type, chat_id)

        if content_type == 'text' and msg['text'] not in bot_commands:
            self.bot.sendMessage(chat_id, msg['text'])
        elif msg['text'] in bot_commands:
            self.parse_command(msg['text'])

        print(telepot.glance(msg, flavor=flavor))

    def parse_command(self, cmd):
        if cmd in bot_commands:
            print("command received: " + cmd)

            if str(cmd).lower() == bot_commands[0].lower():
                self.running = False
