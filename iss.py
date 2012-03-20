#!/usr/bin/env python
# coding=utf-8

# Group:    XXX  
# Version:  0.00  
# Date:     2012-3-20  

# Group Members
# =============
#  - Nick Aldwin <aldwin@ccs.neu.edu>
#  - Eric Chin <???@css.neu.edu>

# For usage, see README.md

import sys, os, binascii, io
from struct import pack, unpack

# Constants
CODE =  0x00001000
ADD  =  0b000000
ADDI =  0b001000
BEQ  =  0b000100
J    =  0b000010
LW   =  0b100011
SW   =  0b101011
HLT  =  0b111111

# Instructions
class add:
    def __init__(self, instr):
        self.rs = slicebin(instr, 25, 21)
        self.rt = slicebin(instr, 20, 16)
        self.rd = slicebin(instr, 15, 11)
        self.shamt = slicebin(instr, 10, 6)
        self.funct = slicebin(instr, 5, 0)

class addi:
    def __init__(self, instr):
        self.rs = slicebin(instr, 25, 21)
        self.rt = slicebin(instr, 20, 16)
        self.imm = slicebin(instr, 15, 0)

class beq:
    def __init__(self, instr):
        self.rs = slicebin(instr, 25, 21)
        self.rt = slicebin(instr, 20, 16)
        self.addr = slicebin(instr, 15, 0)

class lw:
    def __init__(self, instr):
        self.rs = slicebin(instr, 25, 21)
        self.rt = slicebin(instr, 20, 16)
        self.addr = slicebin(instr, 15, 0)

class sw:
    def __init__(self, instr):
        self.rs = slicebin(instr, 25, 21)
        self.rt = slicebin(instr, 20, 16)
        self.addr = slicebin(instr, 15, 0)

class j:
    def __init__(self, instr):
        self.target = slicebin(instr, 25, 0)

class hlt:
    def __init__(self, instr):
        pass


def slicebin(i, high, low):
    mask = 2L**(high - low + 1) -1
    return (i >> low) & mask

def usage():
    """ Prints program usage and exits """
    print """Usage: python iss.py <input>
<input> : input binary program"""
    exit()

def main():
    """ Main operations """
    if len(sys.argv) < 2:
        usage()
    
    infile = sys.argv[1]

    if not os.path.isfile(infile):
        sys.exit("File does not exist: %s" % infile)

    print "input: %s" % infile

    progfile = open(infile, 'rb')
    memory = io.BytesIO()
    instrs = []

    # read memory in chunks of 16 bytes
    while progfile.tell() < CODE:
        memory.write(progfile.read(16))

    # read code
    while True:
        rawinstr = progfile.read(4)
        if rawinstr == '':
            break
        instr = unpack("<I", rawinstr)[0]
        op = slicebin(instr, 31, 26)
        if   op == ADD:
            instrs.append(add(instr))
        elif op == ADDI:
            instrs.append(addi(instr))
        elif op == BEQ:
            instrs.append(beq(instr))
        elif op == J:
            instrs.append(j(instr))
        elif op == LW:
            instrs.append(lw(instr))
        elif op == SW:
            instrs.append(sw(instr))
        elif op == HLT:
            instrs.append(hlt(instr))
        else: # unrecognized instruction
            instrs.append(None)

    # print hexdump
    # (will be removed later)
    hexdump(progfile)

    progfile.close()

def hexdump(progfile):
    print "Hexdump:"
    progfile.seek(0)
    while True:
        pos = progfile.tell()
        bytes = progfile.read(16)
        if bytes == '':
            break
        fullbytes = unpack("<cccccccccccccccc", bytes)
        print (hex(pos)[2:][:-1]).zfill(8) + '  ' + ' '.join(map(lambda b: binascii.hexlify(b), fullbytes))

if __name__ == '__main__':
    main()
