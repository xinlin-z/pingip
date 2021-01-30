import sys
import argparse
import concurrent.futures as cuf
import subprocess
import time
import re
from ipaddress import ip_network


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


def ping_one_ip(ip, count):
    stdout = shell('ping -c %d -W 1 %s' % (count,ip))
    rnum = re.search(r'(\d) received', stdout)
    if (pn:=rnum.groups()[0]) == '0':
        return None
    return f'{ip} {pn}/{count}'


def ping_all(net, count, worker_num):
    tpool = eval('cuf.ThreadPoolExecutor() if worker_num is None'
                 ' else cuf.ThreadPoolExecutor(worker_num)')
    all_task = []
    for ip in ip_network(net).hosts():
        all_task.append(tpool.submit(ping_one_ip, str(ip), count))
    num = 0
    for it in cuf.as_completed(all_task):
        if rt:=it.result():
            print(rt)
            num += 1
            cprint(' Found IP: %d'%num, end='\r', fg='k',bg='r')
    cprint(' Found IP: %d'%num, fg='k',bg='r')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--net', help='network address/mask')
    parser.add_argument('-c', type=int, default=2, help='count of ping')
    parser.add_argument('-w', type=int, help='how many ping worker')
    args = parser.parse_args()
    ping_all(args.net, args.c, args.w)


if __name__ == '__main__':
    main()
