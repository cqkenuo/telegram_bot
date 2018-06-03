bot_commands = ["/scan", "/monitor", "/arp", "/prev", "/trace", "/reg", "/help",
                "/img", "/r34", "/clear", "/log", "/live", "/mybb", "/b", "/dns",
                "/logs", "/clear_logs"]

restricted_commands = ["/monitor", "/arp", "/trace", "/clear"]

command_descriptions = ['Performs a port scan on the specified address passed as a parameter i.e. /scan <ip address>',
                        'Sniffs the packets on the host machine running the script. '
                        'Packet count to return is an optional parameter i.e. /monitor <number>',
                        'Performs a network scan for all the devices connected to the script hosts network',
                        'Calls the previously received command',
                        'Runs a traceroute to the specified website/address',
                        'Registers the user as an admin only if a valid key is passed as a parameter',
                        'Returns a list of available commands with descriptions',
                        'Returns a random image result from the search (safe search is off by default)',
                        'Performs an r34 search for the provided search term',
                        'Clears any cache arrays present',
                        'Returns the debugging log file (personal information still saved in this version of the bot)',
                        'Returns a random result from the specified live leak search',
                        'Returns the specified number (default 5) of the latest articles from the MyBroadband website',
                        'Pulls a random image from 4chan.org/b (use at own peril)',
                        'Performs a DNS lookup on the provided hostname',
                        'Returns the backed-up log files',
                        'Deletes the backed up log files']
