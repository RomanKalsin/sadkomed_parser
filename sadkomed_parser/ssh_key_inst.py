#!/usr/bin/env python3


import pexpect
import getpass
from colorama import init, Fore


init(autoreset=True)
green = Fore.GREEN
red = Fore.RED


def inst_on_host(ssh, password):
    ans0 = "password:"
    ans1 = 'were skipped because they already'
    ans2 = 'No route to host'
    ans3 = 'e you want to continue connecting'
    ans4 = 'Now try logging into the machine'
    ans5 = 'publickey,password'
    i = ssh.expect([ans0, ans1, ans2, ans3, ans4, ans5])
    if i == 0:
        ssh.sendline(password)
        inst_on_host(ssh, password)
    elif i == 1:
        print(green + 'Key exist on host')
    elif i == 2:
        print(red + 'Host no exist')
    elif i == 3:
        ssh.sendline('yes')
        inst_on_host(ssh, password)
    elif i == 4:
        print(green + "Key installed to host")
    elif i == 5:
        print(red + "Permission denied")


def key_install(data, groups, cred):
    for sect in groups:
        print(sect)
        is_user = cred[sect].get("ansible_ssh_user")
        is_pass = cred[sect].get("ansible_ssh_pass")
        if is_user and is_pass:
            user = cred[sect]["ansible_ssh_user"]
            password = cred[sect]["ansible_ssh_pass"]
        elif is_user and not is_pass:
            user = cred[sect]["ansible_ssh_user"]
            password = getpass.getpass()
        elif not is_user and is_pass:
            user = input("Username:")
            password = cred[sect]["ansible_ssh_pass"]
        else:
            user = input("Username:")
            password = getpass.getpass()
        for key in data[sect]:
            ip = data[sect][key]
            print("{} = {}".format(key, ip))
            ssh = pexpect.spawn("ssh-copy-id {}@{}".format(user, ip))
            inst_on_host(ssh, password)
            ssh.close()
