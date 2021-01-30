import argparse
import concurrent.futures as cuf
import subprocess
import time
import re
from ipaddress import ip_network


def shell(cmd, cwd=None):
    """Run a shell cmd, return stdout+stderr, or raise, no need 2>&1."""
    proc = subprocess.run(cmd, shell=True, cwd=cwd,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise ChildProcessError(proc.stdout.decode())
    return proc.stdout.decode()


def ping_one_ip(ip):
    try:
        stdout = shell('ping -c 1 -W 1 %s' % ip)
    except:
        return None
    return ip


def ping_all(subnet):
    tpool = cuf.ThreadPoolExecutor()
    all_task = []
    for ip in ip_network(subnet).hosts():
        all_task.append(tpool.submit(ping_one_ip, ip))
    num = 0
    for it in cuf.as_completed(all_task):
        if rt:=it.result():
            print(rt)
            num += 1
    print('Done, %d'%num)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('subnet')
    args = parser.parse_args()
    ping_all(args.subnet)
    

if __name__ == '__main__':
    main()
