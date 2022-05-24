#!/usr/bin/env python3


from sadkomed_parser.cli import cli
from sadkomed_parser.ssh_key_inst import key_install


def command_handler():
    options = cli()
    if options.keys:
        key_install(options.inventory, options.group)
