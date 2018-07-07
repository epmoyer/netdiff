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
    # pp = pprint.PrettyPrinter(indent=3)
    # pp.pprint(nets)
    for net in nets:
        print(net)


def get_nets(filname):
    with open(filname) as f:
        content = f.readlines()
    nets = []
    net = None
    for line in content:
        line = line.rstrip('\n')
        if line.startswith('*SIGNAL*'):
            if net:
                nets.append(net)
            # net = {'name': line.replace('*SIGNAL* ', ''), 'nodes':[]}
            net_name = line.replace('*SIGNAL* ', '')
            net = Net(net_name)
            continue
        if net:
            if line.startswith('*'):
                nets.append(net)
                net = None
                continue
            else:
                # net['nodes'] += line.strip().split(' ')
                nodes = line.strip().split(' ')
                net.add_nodes(nodes)
    return nets

class Net:
    def __init__(self, name, nodes=None):
        self.name = name
        self.nodes = [] if nodes is None else nodes

    def add_nodes(self, nodes):
        self.nodes += nodes

    def __repr__(self):
        return f"Net('{self.name}', {self.nodes})"

    def __str__(self):
        return f'{self.name}: {", ".join(self.nodes)}'

if __name__ == '__main__':
    main()
