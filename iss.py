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

import sys, os
from struct import pack, unpack

# Constants
CODE =  0x00001000

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

if __name__ == '__main__':
    main()
