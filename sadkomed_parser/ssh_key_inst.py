#!/usr/bin/env python3


import pexpect
import getpass
from sadkomed_parser.key_exist import key_exist
from sadkomed_parser.inventory_list import open_inventory


def key_install(inventory, group):
    if key_exist():
        data, groups = open_inventory(inventory, group)
        password = getpass.getpass()
        for sect in groups:
            print(sect)
            for key in data[sect]:
                ip = data[sect][key]
                print("{} = {}".format(key, ip))
                print('connect to {}'.format(ip))
                ssh = pexpect.spawn("ssh-copy-id root@{}".format(ip))
                ans0 = "password:"
                ans1 = 'WARNING: All keys were skipped because they already'
                ans2 = 'No route to host'
                ans3 = 'Are you sure you want to continue connecting'
                i = ssh.expect([ans0, ans1, ans2, ans3])
                if i == 0:
                    ssh.sendline(password)
                    ssh.expect('Now try logging into the machine')
                    print("key installed to host {}".format(ip))
                elif i == 1:
                    print('key exist on host {}'.format(ip))
                elif i == 2:
                    print('host {} no exist'.format(ip))
                elif i == 3:
                    ssh.sendline('yes')
                    ssh.expect("password:")
                    ssh.sendline(password)
                    ssh.expect('Now try logging into the machine')
                    print("key installed to host {}".format(ip))
                ssh.close()
            print("OK")
