#!/usr/bin/env python3

# Standard library
from textwrap import indent

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
    # nets = get_nets(arguments['<file1>'])
    # for net in nets:
    #     print(net)
    netlist_left = Netlist(arguments['<file1>'])
    netlist_left.dump()

# def get_nets(filname):
#     with open(filname) as f:
#         content = f.readlines()
#     nets = []
#     net = None
#     for line in content:
#         line = line.rstrip('\n')
#         if line.startswith('*SIGNAL*'):
#             if net:
#                 nets.append(net)
#             # net = {'name': line.replace('*SIGNAL* ', ''), 'nodes':[]}
#             net_name = line.replace('*SIGNAL* ', '')
#             net = Net(net_name)
#             continue
#         if net:
#             if line.startswith('*'):
#                 nets.append(net)
#                 net = None
#                 continue
#             else:
#                 # net['nodes'] += line.strip().split(' ')
#                 nodes = line.strip().split(' ')
#                 net.add_nodes(nodes)
#     return nets

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

class Netlist:
    def __init__(self, filename):
        self.filename = filename
        self.nets = []
        with open(filename) as f:
            content = f.readlines()
        net = None
        for line in content:
            line = line.rstrip('\n')
            if line.startswith('*SIGNAL*'):
                if net:
                    self.nets.append(net)
                net_name = line.replace('*SIGNAL* ', '')
                net = Net(net_name)
                continue
            if net:
                if line.startswith('*'):
                    self.nets.append(net)
                    net = None
                    continue
                else:
                    nodes = line.strip().split(' ')
                    net.add_nodes(nodes)
        
    def dump(self):
        print(self.filename)
        for net in self.nets:
            print(net)


if __name__ == '__main__':
    main()
