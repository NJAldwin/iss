#!/usr/bin/env python
# coding=utf-8

# Group:    Astronauts  
# Version:  0.01  
# Date:     2012-3-20  

# Group Members
# =============
#  - Nick Aldwin <aldwin@ccs.neu.edu>
#  - Eric Chin <chiner@css.neu.edu>

# For usage, see README.md

import sys, os, binascii, io
from struct import pack, unpack

# Constants
CODE =  0x00001000
NOP  =  0
ADD  =  0b000000
ADDI =  0b001000
BEQ  =  0b000100
J    =  0b000010
LW   =  0b100011
SW   =  0b101011
HLT  =  0b111111

# Debug Info
DEBUG = False

# Instructions
class instruction(object):
    def __init__(self, instr):
        self.rs = slicebin(instr, 25, 21)
        self.rt = slicebin(instr, 20, 16)
        self.rd = slicebin(instr, 15, 11)
        self.shamt = slicebin(instr, 10, 6)
        self.funct = slicebin(instr, 5, 0)
        self.imm = slicebin(instr, 15, 0)
        self.addr = slicebin(instr, 15, 0)
        self.target = slicebin(instr, 25, 0)
        
class add(instruction):
    def __init__(self, instr):
        super(add, self).__init__(instr)
    def __str__(self):
        return "add $%s, $%s, $%s" % (self.rd, self.rs, self.rt)

class addi(instruction):
    def __init__(self, instr):
        super(addi, self).__init__(instr)
    def __str__(self):
        return "addi $%s, $%s, %s" % (self.rt, self.rs, self.imm)

class beq(instruction):
    def __init__(self, instr):
        super(beq, self).__init__(instr)
    def __str__(self):
        return "beq $%s, $%s, %s" % (self.rs, self.rt, self.imm)

class lw(instruction):
    def __init__(self, instr):
        super(lw, self).__init__(instr)
    def __str__(self):
        return "lw $%s, %s($%s)" % (self.rt, self.imm, self.rs)

class sw(instruction):
    def __init__(self, instr):
        super(sw, self).__init__(instr)
    def __str__(self):
        return "sw $%s, %s($%s)" % (self.rt, self.imm, self.rs)

class j(instruction):
    def __init__(self, instr):
        super(j, self).__init__(instr)
    def __str__(self):
        return "j %s" % (self.target - (CODE >> 2))

class hlt(instruction):
    def __init__(self, instr):
        super(hlt, self).__init__(instr)
    def __str__(self):
        return "hlt"

class nop(instruction):
    def __init__(self, instr):
        super(nop, self).__init__(instr)
    def __str__(self):
        return "noop"

# Structure for pipeline stages

class pipeline_register:
    def __init__(self, **kwds):
        self.instr = nop(0) # all pipeline registers store an instruction
    	self.__dict__.update(kwds)


def slicebin(i, high, low):
    """ Returns [high,low] bits of the binary number"""
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

    progfile = open(infile, 'rb')

    # Storage Units
    memory = io.BytesIO()
    instrs = []
    pc     = 0
    regs   = [0] * 32
    
    # Pipeline Registers / Stages
    IF_ID = pipeline_register()
    ID_EX = pipeline_register()
    EX_MEM = pipeline_register()
    MEM_WB = pipeline_register()

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
        if   instr == NOP:
            instrs.append(nop(instr))
        elif op == ADD:
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
            instrs.append(nop(instr))

    # print hexdump
    # (will be removed later)
    #hexdump(progfile)

    progfile.close()

    # dump decompilation (only instructions)
    f = open("src.s", "w")
    f.write(decompile(instrs))
    f.close()

    # reset pipeline registers
    IF_ID.npc = 0

    cycles = 0
    ninstr = 0

    # run simulator
    while True:
        # clock cycle
        printifd("-----clock-----")
        cycles += 1
        
        # ----WB
        printifd("-wb-")
        instr = MEM_WB.instr
        if   isinstance(instr, add):
            regs[instr.rd] = MEM_WB.aluout
        elif isinstance(instr, addi):
            regs[instr.rt] = MEM_WB.aluout
        elif isinstance(instr, lw):
            regs[instr.rt] = MEM_WB.lmd
        elif isinstance(instr, hlt):
            printifd("breaking")
            break # todo: should this be somewhere else?  EC: i think this is right
        else:
            pass
        # ----MEM
        printifd("-mem-")
        instr = EX_MEM.instr
        if   isinstance(instr, lw):
            memory.seek(EX_MEM.aluout)
            # todo: make sure the below code actually reads 4 bytes
            printifd("load at %s" % hex(EX_MEM.aluout))
            rd = memory.read(4)
            MEM_WB.lmd = unpack("<I", rd)[0]
        elif isinstance(instr, sw):
            memory.seek(EX_MEM.aluout)
            printifd("write %s at %s" % (EX_MEM.b, hex(EX_MEM.aluout)))
            # todo: make sure the code below actually writes 4 bytes in the correct order
            bts = pack("<I", EX_MEM.b)
            memory.write(bts)
        elif isinstance(instr is add or instr, addi):
            MEM_WB.aluout = EX_MEM.aluout
        else:
            pass
        MEM_WB.instr = instr
        # ----EX
        printifd("-ex-")
        instr = ID_EX.instr
        if   isinstance(instr, add):
            EX_MEM.aluout = ID_EX.a + ID_EX.b
        elif isinstance(instr, addi):
            EX_MEM.aluout = ID_EX.a + ID_EX.imm
        elif isinstance(instr is lw or instr, sw):
            EX_MEM.aluout = ID_EX.a + ID_EX.imm
            EX_MEM.b = ID_EX.b
        elif isinstance(instr, hlt):
            pass # todo: halt here?
        else:
            pass
            
        EX_MEM.instr = instr
        # ----ID
        printifd("-id-")
        instr = IF_ID.instr
        ID_EX.instr = instr
        ID_EX.npc = IF_ID.npc
        ID_EX.a = regs[instr.rs]
        ID_EX.b = regs[instr.rt]
        ID_EX.imm = instr.imm # todo: sign extend?
        
        if isinstance(instr, beq):
            printifd("BRANCH! %s if %s=%s" % (ID_EX.npc + ID_EX.imm, ID_EX.a, ID_EX.b))
            ID_EX.aluout = ID_EX.npc + ID_EX.imm
            ID_EX.cond = (ID_EX.a == ID_EX.b)
        elif isinstance(instr, j):
            naddr = instr.target - (CODE >> 2)
            # todo: are we using the right PC here?
            # todo: is this the right place in the pipeline for a jump?
            naddr = (pc & 0xf0000000) | naddr
            printifd("JUMP! %s" % hex(naddr))
            # todo: is this the right way to jump?
            ID_EX.jmp = True
            ID_EX.jmpaddr = naddr

        # ----IF
        printifd("-if-")
        if isinstance(ID_EX.instr, beq) and ID_EX.cond == True:
            printifd("branching to %s" % ID_EX.aluout)
            pc = ID_EX.aluout
        elif isinstance(ID_EX.instr, j) and ID_EX.jmp == True:
            printifd("jumping to %s" % ID_EX.jmpaddr)
            pc = ID_EX.jmpaddr
        else:
            pc = pc + 1
        instr = instrs[pc]
        if not isinstance(instr, nop):
            # TODO: should this include noops?
            ninstr += 1
        printifd("instr %s: %s" % (pc, instr))
        IF_ID.instr = instr
        IF_ID.npc = pc + 1

    if DEBUG:
        print
        print
        hexdump(memory)
        print

    # final output
    print "-"*35 + "Statistics" + "-"*35
    print "Total # of cycles: %s" % cycles
    print "Total # of instructions: %s" % ninstr
    print "CPI: %s" % (float(cycles)/ninstr)
    print_regs(regs)

def hexdump(progfile):
    """ Dump the file in hex format """
    print "Hexdump:"
    progfile.seek(0)
    while True:
        pos = progfile.tell()
        bytes = progfile.read(16)
        if bytes == '':
            break
        fullbytes = unpack("<cccccccccccccccc", bytes)
        print "%08X" % pos + '  ' + ' '.join(map(lambda b: binascii.hexlify(b), fullbytes))

def decompile(instrs):
    """ Output pseudo source code """
    return "# for debug use only!\n" + "\n".join("%s: %s" % (i, str(instrs[i])) for i in range(0,len(instrs)))
        
def print_regs(regs):
    """ Output values for the registers """
    def fmtreg(n):
        return "R%s: 0x%08X" % (n, regs[n])
    print "Register file contents:"
    print
    for r in range(0, len(regs), 2):
        print "%s %s" % (fmtreg(r), fmtreg(r+1))

def printifd(s):
    """ Prints the string if DEBUG is True """
    if DEBUG:
        print s

if __name__ == '__main__':
    main()
