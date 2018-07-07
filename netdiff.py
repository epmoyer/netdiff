#!/usr/bin/env python3

# Standard library
import pprint

# Library
from docopt import docopt

USAGE = (
"""Usage:
    netdiff <file1> <file2>
    netdiff -h | --help
    netdiff --version

Options:
  -h --help               Show this screen.
  --version               Show version
""")

__version__ = '0.1.0'

def main():
    arguments = docopt(USAGE, version=__version__)
    nets = get_nets(arguments['<file1>'])
    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(nets)


def get_nets(filname):
    with open(filname) as f:
        content = f.readlines()
    nets = []
    net = None
    in_signal = False
    for line in content:
        line = line.rstrip('\n')
        if line.startswith('*SIGNAL*'):
            if net:
                nets.append(net)
            net = {'name': line.replace('*SIGNAL* ', ''), 'nodes':[]}
            continue
        if net:
            if line.startswith('*'):
                nets.append(net)
                net = None
                continue
            else:
                net['nodes'] += line.strip().split(' ')
    return nets

if __name__ == '__main__':
    main()