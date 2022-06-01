#!/usr/bin/env python3


from sadkomed_parser.cli import cli
from sadkomed_parser.ssh_key_inst import key_install
from sadkomed_parser.inventory_list import open_inventory
from sadkomed_parser.key_exist import key_exist


# Condition for executing commands
def command_handler():
    options = cli()
    data, groups, cred = open_inventory(options.inventory, options.group)
    if options.keys and key_exist():
        key_install(data, groups, cred)
    else:
        print(groups)
