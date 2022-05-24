#!/usr/bin/env python3


import configparser


# Open the inventory file and execute the code on each host
def open_inventory(path, group):
    data = configparser.ConfigParser()
    data.read(path)
    if group == "ALL":
        groups = data.sections()
    else:
        groups = [group]
    return data, groups
