#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import argparse


def main():
    parser = argparse.ArgumentParser('')
    parser.add_argument('FILE')
    args = parser.parse_args()
    with open(args.FILE, 'r') as infile:
        lines = infile.read().splitlines()
    pat = r'normalized_time\(.+?\) ?= ?(\d+)'
    first = int(re.findall(pat, lines[-1])[0])
    second = int(re.findall(pat, lines[-2])[0])
    with open(args.FILE + '.flag', 'w') as out:
        if first == second:
            out.write('no')
        else:
            out.write('yes')


if __name__ == '__main__':
    main()
