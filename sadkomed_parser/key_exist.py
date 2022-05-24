#!/usr/bin/env python3


from os.path import isfile, expanduser


def key_exist():
    home = expanduser("~")
    keys = "/.ssh/id_rsa.pub"
    if isfile(home + keys):
        return True
    else:
        print("Create a key on the path: '{}' \
         and try again.".format(home + keys))
        return False
