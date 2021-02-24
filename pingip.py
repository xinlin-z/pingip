import sys
import argparse
import concurrent.futures as cuf
import subprocess
import re
from ipaddress import ip_network
import threading
import queue


def cprint(*objects, sep=' ', end='\n', file=sys.stdout,
           flush=False, fg=None, bg=None, style='default'):
    """colorful print.
    Color and style the string and background, then call the print function,
    Eg: cprint('pynote.net', fg='red', bg='green', style='blink')
    The other parameters are the same with stand print!
    """
    def _ct(code='0'):
        return '\033[%sm'%code

    # text color
    c = 37
    if fg in ('red','r'): c = 31
    elif fg in ('green','g'): c = 32
    elif fg in ('yellow','y'): c = 33
    elif fg in ('blue','b'): c = 34
    elif fg in ('magenta','m'): c = 35
    elif fg in ('cyan','c'): c = 36
    elif fg in ('white','w'): c = 37
    elif fg in ('black','k'): c = 30
    # background color
    b = 40
    if bg in ('red','r'): b = 41
    elif bg in ('green','g'): b = 42
    elif bg in ('yellow','y'): b = 43
    elif bg in ('blue','b'): b = 44
    elif bg in ('magenta','m'): b = 45
    elif bg in ('cyan','c'): b = 46
    elif bg in ('white','w'): b = 47
    elif bg in ('black','k'): b = 40
    # style
    a = 0
    if style == 'underline': a = 4
    elif style == 'blink': a = 5
    elif style == 'inverse': a = 7

    string = sep.join(map(str, objects))
    color = '%d;%d;%d' % (a,c,b)
    print(_ct(color)+string+_ct(), sep=sep, end=end, file=file, flush=flush)


def shell(cmd, cwd=None):
    """Run a shell cmd, return stdout+stderr, or raise, no need 2>&1."""
    proc = subprocess.run(cmd, shell=True, cwd=cwd,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.stdout.decode()


def get_ipv4_pair():
    """Return ipv4 addr pairs by scanning the output of 'ip addr' command.
    Return [(ifname1, addr1, mask1),(ifname2, addr2, mask2),...]
    mask is an int in str type for length.
    """
    stdout = shell('ip addr')
    rv = []
    ore_ifname = re.compile(r'^\d+:\s+(\w+):')
    ore_ip = re.compile(r'^inet\s([\d|.]+)/(\d{1,2})')
    name = addr = mask = None
    for line in stdout.split('\n'):
        if name and addr:
            rv.append((name,addr,mask))
            name = addr = mask = None
        ifname = ore_ifname.search(line.strip())
        if ifname:
            name = ifname.groups()[0]
            continue
        ip = ore_ip.search(line.strip())
        if ip:
            addr = ip.groups()[0]
            mask = ip.groups()[1]
            continue
    return rv


qmsg = queue.Queue()
sp = None
ip_num = 0
ip_tnum = 0


def ping_one_ip(ip, count, timeout):
    stdout = shell(f'ping -c {count} -W {timeout} {ip}')
    rnum = re.search(r'(\d) received', stdout)
    try:
        if (pn:=rnum.groups()[0]) == '0':
            qmsg.put((ip,None))
            return
    except AttributeError:
        qmsg.put((ip,None))
        return
    qmsg.put((ip,f'{ip:16} {pn}/{count:<32}'))


def show_completed():
    global ip_num,ip_tnum
    s24 = ' ' * 24
    while rt:=qmsg.get():
        sp.release()
        if rt[0] is None: return
        ip_tnum += 1
        if rt[1]:
            print(rt[1], s24)
            ip_num += 1
        cprint(f' Worker: {threading.active_count()-2},'
               f' Pinging: {rt[0]}, Found IP: {ip_num}/{ip_tnum} ',
               end='\r', flush=True, fg='k',bg='m')


def ping_all(net, count, worker_num, timeout):
    # start show thread
    tshow = threading.Thread(target=show_completed, args=(), daemon=True)
    tshow.start()
    # create thread pool
    tpool = (cuf.ThreadPoolExecutor() if worker_num is None
             else cuf.ThreadPoolExecutor(worker_num))
    # create global semaphore
    global sp
    sp = threading.BoundedSemaphore(tpool._max_workers)
    # submit tasks loop
    for ip in ip_network(net,strict=False).hosts():
        sp.acquire()
        tpool.submit(ping_one_ip, str(ip), count, timeout)
    # wait tpool
    tpool.shutdown()
    # wait tshow
    qmsg.put(None)
    tshow.join()
    # last print
    cprint(f'IP Number: {ip_num}/{ip_tnum:<64}', fg='m')


def main():
    parser = argparse.ArgumentParser()
    net = parser.add_mutually_exclusive_group(required=True)
    net.add_argument('--net', help='network address/mask')
    net.add_argument('--local',action='store_true',help='choose a local port')
    parser.add_argument('-c', type=int, default=2, help='count of ping packet')
    parser.add_argument('-w', type=int, help='how many threaded ping workers')
    parser.add_argument('-t', type=int, default=1, help='timeout in second')
    args = parser.parse_args()
    if args.net:
        ping_all(args.net, args.c, args.w, args.t)
    else:
        ipv4_pair = get_ipv4_pair()
        cprint('Index    Interface,IP,Mask', fg='g')
        for i,v in enumerate(ipv4_pair):
            print(f'{i:^6}   {v}')
        i = int(input('--> choose a local port index: '))
        ping_all(f'{ipv4_pair[i][1]}/{ipv4_pair[i][2]}',args.c,args.w,args.t)


if __name__ == '__main__':
    main()
