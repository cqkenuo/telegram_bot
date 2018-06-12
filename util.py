

# Bytes to MegaBytes
def to_mb(b):
    return '%0.2f' % (b / (1024*1024))


def get_pc_stats():
    import psutil

    msg = 'CPU:\n'
    msg += '===================================\n'

    msg += 'CPU usage (per core):\t\t {}\n'.format(str(psutil.cpu_percent(interval=1, percpu=True)))
    msg += 'Core count:\t\t {}\n'.format(str(psutil.cpu_count(logical=False)))

    cpu_freq = psutil.cpu_freq(percpu=True)
    for item in cpu_freq:
        msg += 'Core frequency:\t\t {} \tmax: {}\n'.format(str(item.current), str(item.max))

    msg += '\nMemory:\n'
    msg += '===================================\n'

    memory = psutil.virtual_memory()
    msg += 'Total:\t\t {} (MB)\n'.format(to_mb(memory.total))
    msg += 'Available:\t\t {} (MB)\n'.format(to_mb(memory.available))
    msg += 'Used:\t\t {} (MB)\n'.format(to_mb(memory.used))
    msg += 'Free:\t\t {} (MB)\n'.format(to_mb(memory.free))

    return msg