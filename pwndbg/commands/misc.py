#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import errno as _errno
import struct

import gdb

import pwndbg as _pwndbg
import pwndbg.arch as _arch
import pwndbg.auxv
import pwndbg.commands
import pwndbg.regs
import pwndbg.symbol

_errno.errorcode[0] = 'OK'

parser = argparse.ArgumentParser(description='''
Converts errno (or argument) to its string representation.
''')
parser.add_argument('err', type=int, nargs='?', default=None, help='Errno; if not passed, it is retrieved from __errno_location')

@_pwndbg.commands.ArgparsedCommand(parser)
def errno(err):
    if err is None:
        # Dont ask.
        errno_location = pwndbg.symbol.get('__errno_location')
        err = pwndbg.memory.int(errno_location)
        # err = int(gdb.parse_and_eval('*((int *(*) (void)) __errno_location) ()'))

    err = abs(int(err))

    if err >> 63:
        err -= (1<<64)
    elif err >> 31:
        err -= (1<<32)

    msg = _errno.errorcode.get(int(err), "Unknown error code")
    print("Errno %i: %s" % (err, msg))

parser = argparse.ArgumentParser(description='''
Prints out a list of all pwndbg commands. The list can be optionally filtered if filter_pattern is passed.
''')
parser.add_argument('filter_pattern', type=str, nargs='?', default=None, help='Filter to apply to commands names/docs')

@_pwndbg.commands.ArgparsedCommand(parser)
def pwndbg(filter_pattern):
    sorted_commands = list(_pwndbg.commands._Command.commands)
    sorted_commands.sort(key=lambda x: x.__name__)

    if filter_pattern:
        filter_pattern = filter_pattern.lower()

    for c in sorted_commands:
        name = c.__name__
        docs = c.__doc__

        if docs: docs = docs.strip()
        if docs: docs = docs.splitlines()[0]

        if not filter_pattern or filter_pattern in name.lower() or (docs and filter_pattern in docs.lower()):
            print("%-20s %s" % (name, docs))

@_pwndbg.commands.ParsedCommand
def distance(a, b):
    '''Print the distance between the two arguments'''
    a = int(a) & _arch.ptrmask
    b = int(b) & _arch.ptrmask

    distance = (b-a)

    print("%#x->%#x is %#x bytes (%#x words)" % (a, b, distance, distance // _arch.ptrsize))

@_pwndbg.commands.Command
def canary():
    """Print out the current stack canary"""
    auxv = _pwndbg.auxv.get()
    at_random = auxv.get('AT_RANDOM', None)
    if at_random is not None:
        print("AT_RANDOM=%#x" % at_random)
    else:
        print("Couldn't find AT_RANDOM")
