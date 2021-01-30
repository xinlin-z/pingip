import concurrent.futures as cuf
import subprocess
import time
import re
import ipaddress


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


exe = cuf.ThreadPoolExecutor(max_workers=300)
all_task = [exe.submit(ping_one_ip, ('192.168.2.%d'%i)) for i in range(1,255)]

num = 0
for it in cuf.as_completed(all_task):
    if rt:=it.result():
        print(rt)
        num += 1

print('Done, %d'%num)
