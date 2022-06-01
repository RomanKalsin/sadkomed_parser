#!/usr/bin/env python3


import argparse


# Argpaser CLI
def cli():
    description_cli = "Proxmox parser, takes an inventory file."
    options = argparse.ArgumentParser(description=description_cli)
    options.add_argument("inventory", help="Path to the inventory file.")
    options.add_argument("-g", "--group", default="ALL",
                         metavar="GROUP",
                         help="Group hosts, default = ALL.")
    options.add_argument("-k", "--keys", action="store_true",
                         help="Install a key on hosts.")
    return options.parse_args()
