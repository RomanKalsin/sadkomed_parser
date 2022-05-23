#!/usr/bin/env python3


import configparser


def open_inventory(path, group):
    data = configparser.ConfigParser()
    data.read(path)
    if group == "ALL":
        groups = data.sections()
    else:
        groups = [group]
    for sect in groups:
        print(sect)
        for key in data[sect]:
            print("{} = {}".format(key, data[sect][key]))
