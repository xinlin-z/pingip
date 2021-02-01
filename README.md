# pingip

It's a ping scan tool that can ping a network and find out all ip addresses
of host which responded. Pingip uses `ping` command to do it's job. Below
are usage examples and parameters explanation.

```shell
$ python3 pingip.py -h
```

```shell
$ python3 pingip.py --local -w 200
Index    Interface,IP,Mask
  0      ('lo', '127.0.0.1', '8')
  1      ('enp3s0', '192.168.1.198', '24')
--> Choose a local port index: 1
192.168.1.1      2/2
192.168.1.121    2/2
192.168.1.123    2/2
192.168.1.198    2/2
192.168.1.199    2/2
IP Number: 5
```

**--local**: list all local interfaces and to ping the whole ip network belong
to the interface you choose.

**-w**: specify the number of ping thread workers, the more workers the faster.

**2/2**: send out 2 ping packages and receive 2 replys.

```shell
$ python3 pingip.py --net 192.168.1.198/24 -w 200 -c 4 -t 2
192.168.1.1      4/4
192.168.1.121    4/4
192.168.1.123    4/4
192.168.1.198    4/4
192.168.1.199    4/4
IP Number: 5
```

**--net**: specify a network to do ping scan.

**-c**: set how many ping package to send, default is 2.

**-t**: set ping timeout in second, default is 1.

```shell
$ python3 pingip.py --net 36.1.36.1/24 -w 500
36.1.36.119      2/2
36.1.36.17       2/2
36.1.36.153      2/2
36.1.36.41       2/2
36.1.36.72       2/2
36.1.36.63       2/2
36.1.36.105      2/2
36.1.36.141      2/2
36.1.36.154      2/2
36.1.36.145      2/2
36.1.36.167      2/2
36.1.36.160      2/2
36.1.36.190      2/2
36.1.36.224      2/2
36.1.36.228      2/2
36.1.36.122      1/2
IP Number: 16
```
