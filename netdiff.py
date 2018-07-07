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

    compare_netlist.diff(baseline_netlist)

    # baseline_netlist.dump_diff()
    # compare_netlist.dump_diff()
    # print()

    column_width = 25
    compare_netlist.dump_parallel_diff(baseline_netlist, column_width)
    

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
        self.nodes.sort()

    def diff_str(self, max_width=25, enable_pad=False):
        diff_color = Fore.RED if self.is_baseline else Fore.GREEN
        diff_symbol = '-' if self.is_baseline else '+'

        text_manager = TextManager(max_width, enable_pad)

        if self.net_differs:
            text_manager.append(f'{diff_symbol}{self.name}: ')
            for node in self.nodes:
                text_manager.append(f'{node}, ')
            text_manager.color_all(diff_color)
            return text_manager.render()
        if not self.differing_nodes:
            text_manager.append(f' {self.name}: ')
            for node in self.nodes:
                text_manager.append(f'{node}, ')
            return text_manager.render()

        text_manager.append(f' {self.name}: ')
        for node in self.nodes:
            if node in self.differing_nodes:
                text_manager.append(f'{diff_symbol}{node}, ', diff_color)
            else:
                text_manager.append(f'{node}, ')
        return text_manager.render()

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

        self.nets.sort(key=lambda x: x.name)

    def dump(self):
        print(self.filename)
        for net in self.nets:
            print(indent(str(net), '   '))

    def dump_diff(self):
        print(self.filename)
        for net in self.nets:
            print(indent(net.diff_str(), '   '))

    def dump_parallel_diff(self, baseline_netlist, column_width):
        compare_netlist = self

        compare_netlist.reset_traverse()
        baseline_netlist.reset_traverse()

        while True:
            baseline_net = baseline_netlist.traverse()
            compare_net = compare_netlist.traverse()

            if baseline_net is None:
                baseline_text = None
            else:
                baseline_text = baseline_net.diff_str(enable_pad=True, max_width=column_width)
            if compare_net is None:
                compare_text = None
            else:
                compare_text = compare_net.diff_str(enable_pad=True, max_width=column_width)

            if baseline_net is None and compare_net is None:
                break
            elif baseline_net is not None and compare_net is None:
                baseline_netlist.advance_traverse()
            elif baseline_net is None and compare_net is not None:
                compare_netlist.advance_traverse()
            elif baseline_net.name < compare_net.name:
                compare_text = None
                baseline_netlist.advance_traverse()
            elif baseline_net.name > compare_net.name:
                baseline_text = None
                compare_netlist.advance_traverse()
            else:
                compare_netlist.advance_traverse()
                baseline_netlist.advance_traverse()
            print_columns(baseline_text, compare_text, column_width)

    def diff(self, baseline_netlist):
        compare_netlist = self

        compare_netlist.clear_diffs(is_baseline=False)
        compare_netlist.reset_traverse()

        baseline_netlist.clear_diffs(is_baseline=True)
        baseline_netlist.reset_traverse()

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


class TextManager():

    def __init__(self, max_width=25, enable_pad=False, indent=4):
        self.lines = []
        self.line = ''
        self.line_width = 0
        self.max_width = max_width
        self.enable_pad = enable_pad
        self.indent = indent

    def append(self, text, color=None):
        if len(text) + self.line_width <= self.max_width:
            # No wrap
            self.line = self._append_to_current_line(self.line, text, color)
        elif self.line_width == 0:
            # Current line is already blank and the requested text does not fit,
            # so use it as-is.
            self.line = self._append_to_current_line('', text, color)
        else:
            # Wrap text
            self._commit_line()
            self.line = self._append_to_current_line('', ' ' * self.indent + text, color)
        # print(f'>>>{self.line}<<< {self.line_width}')

    def render(self):
        self._commit_line()
        return '\n'.join(self.lines)

    def _commit_line(self):
        if self.line_width != 0:
            if self.enable_pad and self.line_width < self.max_width:
                self.line += ' ' * (self.max_width - self.line_width)
            self.lines.append(self.line)
        self.line = ''
        self.line_width = 0

    def _append_to_current_line(self, text, append_text, color):
        self.line_width += len(append_text)
        if color is not None:
            return text + color + append_text + Style.RESET_ALL
        return text + append_text

    def color_all(self, color):
        self._commit_line()
        self.lines = [color + line + Style.RESET_ALL for line in self.lines]

def print_columns(left_text, right_text, column_width):
    assert left_text is not None or right_text is not None
    if left_text:
        left_lines = left_text.split('\n')
    if right_text:
        right_lines = right_text.split('\n')
    if not left_text:
        left_lines = [' ' * column_width] * len(right_lines)
    if not right_text:
        right_lines = [''] * len(left_lines)
    if len(left_lines) < len(right_lines):
        left_lines += [' ' * column_width] * (len(right_lines) - len(left_lines))
    elif len(left_lines) > len(right_lines):
        right_lines += [''] * (len(left_lines) - len(right_lines))
    for left_line, right_line in zip(left_lines, right_lines):
        print(f'{left_line} | {right_line}')

if __name__ == '__main__':
    main()
