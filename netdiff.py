#!/usr/bin/env python3

# Standard library
from textwrap import indent

# Library
from docopt import docopt
from colorama import init, Fore, Style

# Initialize colorama
init()

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

    baseline_netlist = Netlist(arguments['<file1>'])
    compare_netlist = Netlist(arguments['<file2>'])

    baseline_netlist.dump()
    compare_netlist.dump()

    compare_netlist.diff(baseline_netlist)

    baseline_netlist.dump_diff()
    compare_netlist.dump_diff()
    

class Net:
    def __init__(self, name, nodes=None):
        self.name = name
        self.nodes = [] if nodes is None else nodes
        self.is_baseline = True
        self.net_differs = False
        self.differing_nodes = []

    def clear_diffs(self, is_baseline=True):
        self.net_differs = False
        self.differing_nodes = []
        self.is_baseline = is_baseline

    def add_nodes(self, nodes):
        self.nodes += nodes
        # Pads nodes are normally sorted, but sort anyway to guarantee order
        #    for netlist operations like diff
        self.nodes.sort()

    def diff_str(self):
        diff_color = Fore.RED if self.is_baseline else Fore.GREEN
        diff_symbol = '-' if self.is_baseline else '+'

        if self.net_differs:
            return diff_color + diff_symbol + str(self) + Style.RESET_ALL
        if not self.differing_nodes:
            return ' ' + str(self)
        formatted_nodes = []
        for node in self.nodes:
            if node in self.differing_nodes:
                formatted_nodes.append(diff_color + diff_symbol + node + Style.RESET_ALL)
            else:
                formatted_nodes.append(node)
        return f' {self.name}: {", ".join(formatted_nodes)}'

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

    def dump_diff(self):
        print(self.filename)
        for net in self.nets:
            print(indent(net.diff_str(), '   '))

    def diff(self, baseline_netlist):
        compare_netlist = self

        compare_netlist.clear_diffs(is_baseline=False)
        baseline_netlist.clear_diffs(is_baseline=True)

        while True:
            baseline_net = baseline_netlist.traverse()
            compare_net = compare_netlist.traverse()

            if baseline_net is None and compare_net is None:
                break
            elif baseline_net is not None and compare_net is None:
                baseline_net.net_differs = True
                baseline_netlist.advance_traverse()
                continue
            elif baseline_net is None and compare_net is not None:
                compare_net.net_differs = True
                compare_netlist.advance_traverse()
                continue
            elif baseline_net.name < compare_net.name:
                baseline_net.net_differs = True
                baseline_netlist.advance_traverse()
                continue
            elif baseline_net.name > compare_net.name:
                compare_net.net_differs = True
                compare_netlist.advance_traverse()
                continue
            else:
                # The net names are the same.  Compare the nodes
                for node in baseline_net.nodes:
                    if node not in compare_net.nodes:
                        baseline_net.differing_nodes.append(node)
                for node in compare_net.nodes:
                    if node not in baseline_net.nodes:
                        compare_net.differing_nodes.append(node)
                compare_netlist.advance_traverse()
                baseline_netlist.advance_traverse()

    def clear_diffs(self, is_baseline):
        self.is_baseline = is_baseline
        for net in self.nets:
            net.clear_diffs(is_baseline=is_baseline)

    def reset_traverse(self):
        self._index_next_net = 0

    def traverse(self):
        if self._index_next_net >= len(self.nets):
            return None
        return self.nets[self._index_next_net]

    def advance_traverse(self):
        self._index_next_net += 1

if __name__ == '__main__':
    main()
