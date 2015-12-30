#!/usr/bin/python
#
# This program converts a infinity game board into an smt2 formula.
# Use --help to get a description of the arguments. The input file
# uses the following symbols:
#
# - '0' represents a blank
# - '1' represents one connection
# - '|' represents a line
# - 'L' represents an angle connector
# - 'T' represents a connector with three outputs
# - '+' represents a connector with four outputs
#
# The file should have one line for each row in the puzzle. All of
# the lines should be the same length.
#

import os

def isTrue(x):
    return x
def isFalse(x):
    return "(not %s)" % x
def allof(xs):
    return '(and %s)' % ' '.join(xs)
def oneof(xs):
    return '(or %s)' % ' '.join(xs)

def edge(i):
    return 'edge_%d' % i

def up(row, col):
    return edge(row * (2*COLS + 1) + col)

def down(row, col):
    return edge((row + 1) * (2*COLS + 1) + col)

def left(row, col):
    return edge(row * (2*COLS + 1) + COLS + col)

def right(row, col):
    return edge(row * (2*COLS + 1) + COLS + col + 1)

def constraint0(up, down, left, right):
    return allof([isFalse(up), isFalse(down), isFalse(left), isFalse(right)])

def constraint1(up, down, left, right):
    return oneof([ allof([isTrue(up), isFalse(down), isFalse(left), isFalse(right)])
                 , allof([isFalse(up), isTrue(down), isFalse(left), isFalse(right)])
                 , allof([isFalse(up), isFalse(down), isTrue(left), isFalse(right)])
                 , allof([isFalse(up), isFalse(down), isFalse(left), isTrue(right)]) ])

def constraint_line(up, down, left, right):
    return oneof([ allof([isFalse(up), isFalse(down),
                          isTrue(left), isTrue(right)])
                 , allof([isTrue(up), isTrue(down),
                          isFalse(left), isFalse(right)]) ])

def constraint_elbow(up, down, left, right):
    return oneof([ allof([isTrue(up), isTrue(left),
                          isFalse(down), isFalse(right)])
                 , allof([isTrue(up), isTrue(right),
                          isFalse(down), isFalse(left)])
                 , allof([isTrue(down), isTrue(left),
                          isFalse(up), isFalse(right)])
                 , allof([isTrue(down), isTrue(right),
                          isFalse(up), isFalse(left)]) ])

def constraint3(up, down, left, right):
    return oneof([ allof([ isTrue(up), isTrue(down), isTrue(left), isFalse(right)])
                 , allof([ isTrue(up), isTrue(down), isFalse(left), isTrue(right)])
                 , allof([ isTrue(left), isTrue(right), isTrue(up), isFalse(down)])
                 , allof([ isTrue(left), isTrue(right), isFalse(up), isTrue(down)]) ])

def constraint4(up, down, left, right):
    return allof([ isTrue(up), isTrue(down), isTrue(left), isTrue(right) ])

def read_board(inf):
    lines = [x.replace('\r', '').replace('\n','') for x in inf.readlines()]
    while lines[-1].strip() == '':
        lines = lines[:-1]
    for x in lines:
        assert len(lines[0]) == len(x)
    return lines


def to_sat(inst):
    global ROWS, COLS
    ROWS = len(inst)
    COLS = len(inst[0])

    result = []
    all_vars = set([])

    for i in range(0, ROWS):
        for j in range(0, COLS):
            all_vars = all_vars.union(set([up(i,j), down(i,j), left(i,j), right(i,j)]))
            if inst[i][j] == '0':
                result.append(constraint0(up(i,j), down(i,j), left(i,j), right(i,j)))
            elif inst[i][j] == '1':
                result.append(constraint1(up(i,j), down(i,j), left(i,j), right(i,j)))
            elif inst[i][j] == '|':
                result.append(constraint_line(up(i,j), down(i,j), left(i,j), right(i,j)))
            elif inst[i][j] == 'L':
                result.append(constraint_elbow(up(i,j), down(i,j), left(i,j), right(i,j)))
            elif inst[i][j] == 'T':
                result.append(constraint3(up(i,j), down(i,j), left(i,j), right(i,j)))
            elif inst[i][j] == '+':
                result.append(constraint4(up(i,j), down(i,j), left(i,j), right(i,j)))
            else:
                assert False

    for i in range(0, ROWS):
        result.append(isFalse(left(i,0)))
        result.append(isFalse(right(i,COLS-1)))
    for i in range(0, COLS):
        result.append(isFalse(up(0, i)))
        result.append(isFalse(down(ROWS-1, i)))

    return (all_vars, result)

def to_z3(out, vs, csts):
    for x in vs:
        out.write('(declare-fun %s () Bool)\n' % x)
    for c in csts:
        out.write('(assert %s)\n' % c)
    out.write('(check-sat)\n')
    out.write('(get-model)')

import re

def read_model(inf):
    ptrn = re.compile(r'\(define-fun (edge_[0-9]+)\s+\(\)\s+Bool\s+(false|true)\)')
    result = {}
    for (i,v) in ptrn.findall(inf):
        result[i] = v=='true'
    return result

import subprocess

def solve(board, dump=None):
    (r,w) = os.pipe()

    (vs, csts) = to_sat(board)
    to_z3(os.fdopen(w, 'w'), vs, csts)
    if not dump is None:
        to_z3(dump, vs, csts)
        dump.write('\r\n')
    raw_result = subprocess.check_output(['z3', '-smt2', '-in'],
                                         stdin=r)

    return read_model(raw_result)

# right left down up
TABLE = { 0b0000 : ' '
        , 0b0001 : unichr(0x2579)
        , 0b0010 : unichr(0x257B)
        , 0b0011 : unichr(0x2503)
        , 0b0100 : unichr(0x2578)
        , 0b0101 : unichr(0x251B)
        , 0b0110 : unichr(0x2513)
        , 0b0111 : unichr(0x252B)
        , 0b1000 : unichr(0x257A)
        , 0b1001 : unichr(0x2517)
        , 0b1010 : unichr(0x250F)
        , 0b1011 : unichr(0x2523)
        , 0b1100 : unichr(0x2501)
        , 0b1101 : unichr(0x253B)
        , 0b1110 : unichr(0x2533)
        , 0b1111 : unichr(0x254B) }

def print_board(out, rows, cols, at_intersect):
    for r in range(0,rows):
        for c in range(0,cols):
            val = int(at_intersect[up(r,c)])     \
                | int(at_intersect[down(r,c)])*2 \
                | int(at_intersect[left(r,c)])*4 \
                | int(at_intersect[right(r,c)])*8
            out.write(TABLE[val])
        out.write('\r\n')

import sys

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser('loop.py')
    parser.add_argument('--in', default=False,
                        action='store_true', help='read from standard input')
    parser.add_argument('--dump', action='store_const',
                        const=sys.stderr, help='dump smt problem to standard error')
    parser.add_argument('file', help='the file the read the problem from')

    res = vars(parser.parse_args(sys.argv[1:]))
    if res['in']:
        board = read_board(sys.stdin)
    else:
        board = read_board(file(res['file']))
    answer = solve(board, dump=res['dump'])
    print_board(sys.stdout, ROWS, COLS, answer)
