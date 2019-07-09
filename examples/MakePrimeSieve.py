#!/usr/local/bin/python2

# MakePrimeSieve.py

# Outputs a SMETANA To Infinity! program that computes all
# primes up to a limit specified as an argument to this script.

# See http://esolangs.org/wiki/SMETANA_To_Infinity!

# Part of the Smetana2Infinity.py distribution available from
# https://github.com/anthonykozar/Smetana2Infinity

# Implemented by
# Anthony Kozar
# July 8, 2019

import argparse

# get max integer limit from 1st commandline argument if given
parser = argparse.ArgumentParser(description="Outputs a prime sieve program in SMETANA To Infinity!")
parser.add_argument("max", help="Search for primes up to max", type=int, default=100)
args = parser.parse_args()

maxn = args.max
maxsqrd = maxn**2

print """# Prime number sieve
# Finds primes up to %d.

# Steps 2-%d represent the positive integers to test.
# A step is changed to a NOP after it has been ruled out
# as composite.""" % (maxn, maxn)

print "Step n. Go to step %dn." % maxsqrd
print
print "# Start search with step 2."
print "Step 1. Swap step 1 with step 1."
print
print "# Steps %d-%d are NOPs to be swapped with steps 2-%d." % (maxn+2, maxsqrd-1, maxn)
print "Step n + %d. Swap step 1 with step 1." % maxn
print
print "# All steps %d+ not explicitly defined below are also NOPs." % maxsqrd
print "Step n + %d. Swap step 1 with step 1." % maxsqrd
print

print """# A %dn to %dn+%d block is called when n is found to be prime.
# To keep multiple step number expressions from evaluating to the same
# n, these blocks must be spaced at least every MAX^2 steps where MAX
# is the largest number to be checked for primeness.
""" % (maxsqrd, maxsqrd, maxn+1)

print "# First output the number."
print "Step %dn. Output character n." % maxsqrd
print
print """# Multiples of step n are composite, so change them to NOPs.
# Some steps between 2-%d will be swapped multiple times, so
# for each base n a different set of NOP steps are used.
# A line (%d+m)n is needed below for each m up to MAX/2.""" % (maxn, maxsqrd)

for i in xrange(2, maxn/2 + 1):
	print "Step %dn. Swap step %dn with step %dn + %d." % (maxsqrd+i, i, maxn+i, maxn)

print
print "# Find the next non-composite number."
print "Step %dn + %d. Go to step n + 1." % (maxsqrd, maxn+1)
print
print "# Stop when we pass %d." % maxn
print "Step %d. Stop." % (maxn+1)
