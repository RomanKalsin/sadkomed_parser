#!/usr/bin/env python3


from sadkomed_parser.cli import cli
from sadkomed_parser.inventory_list import open_inventory


def main():
    options = cli()
    open_inventory(options.inventory, options.group)


if __name__ == '__main__':
    main()
