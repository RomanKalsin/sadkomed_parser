#!/usr/bin/env python3


import configparser
import re


# Opening an inventory file and preparing data for check in 
def open_inventory(path, group):
    data = configparser.ConfigParser()
    data.read(path)
    keys = data.sections()
    groups = []
    cred = {}
    for key in keys:
        is_vars = re.search(r':vars', key)
        if not is_vars:
            groups.append(key)
        else:
            up = [option for option in data[key]]
            no_vars = re.search(r'.*(?=:vars)', key).group(0)
            cred[no_vars] = {}
            for c in up:
                is_qotes = re.search(r"(?<=('|\")).*(?=('|\"))", data[key][c])
                if is_qotes:
                    cred[no_vars][c] = is_qotes.group(0)
                    print(is_qotes.group(0))
                else:
                    cred[no_vars][c] = data[key][c]
                    print(data[key][c])
    if group != "ALL":
        groups = [group]

    return data, groups, cred
