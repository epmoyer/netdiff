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

    netlist_left = Netlist(arguments['<file1>'])
    netlist_left.dump()

class Net:
    def __init__(self, name, nodes=None):
        self.name = name
        self.nodes = [] if nodes is None else nodes
        self.is_baseline = True
        self.net_differs = False
        self.differing_nodes = []

    def clear_diffs(self):
        self.net_differs = False
        self.differing_nodes = []

    def add_nodes(self, nodes):
        self.nodes += nodes
        # Pads nodes are normally sorted, but sort anyway to guarantee order
        #    for netlist operations like diff
        self.nodes.sort(key=lambda x: x.name)

    def __repr__(self):
        return f"Net('{self.name}', {self.nodes})"

    def __str__(self):
        return f'{self.name}: {", ".join(self.nodes)}'

class Netlist:
    def __init__(self, filename):
        self.filename = filename
        self.nets = []
        self.is_baseline = True
        self._index_next_net = 0

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

        # Pads netlists are normally sorted, but sort anyway to guarantee order
        #    for netlist operations like diff
        self.nets.sort(key=lambda x: x.name)

    def dump(self):
        print(self.filename)
        for net in self.nets:
            print(indent(str(net), '   '))

    def diff(self, baseline):
        self.clear_diffs(is_baseline=False)
        baseline.clear_diffs(is_baseline=True)

        done = False
        

    def clear_diffs(self, is_baseline):
        self.is_baseline = is_baseline
        for net in self.nets:
            net.clear_diffs()

    def reset_traverse(self):
        self._index_next_net = 0

    def traverse(self):
        if self._index_next_net >= len(self.nets):
            return None
        next_net = self.nets[self._index_next_net]
        self._index_next_net += 1
        return next_net

if __name__ == '__main__':
    main()
