#!/usr/bin/env python

# Smetana2Infinity.py

# An interpreter for the language "SMETANA To Infinity!"
# created by Tanner Swett, after SMETANA by Chris Pressey.

# http://esolangs.org/wiki/SMETANA_To_Infinity!
# https://catseye.tc/article/Automata.md#smetana

# Implemented by
# Anthony Kozar
# June 22-26 and July 4-5, 2019

import sys
import argparse

def printerr(message, line, linenum):
    sys.stderr.write("Error: " + message + " on line " + linenum + ":\n")
    sys.stderr.write("   " + line + '\n')

def parsererr(message, stepnum, tokens, tokidx):
    sys.stderr.write("Error: " + message + " in step " + expr2str(stepnum) + ":\n")
    # print up to 10 tokens for context
    lastidx = min(tokidx + 10, len(tokens))
    sys.stderr.write("   " + " ".join(map(str, tokens[tokidx:lastidx])) + '\n')

def warning(message):
    sys.stderr.write("Warning: " + message + '\n')

# Token constants
DOT = '.'
PLUS = '+'
N = 'N'
STEP = 'Step'
STOP = 'Stop'
GO = 'Go'
TO = 'To'
SWAP = 'Swap'
WITH = 'With'
OUTPUT = 'Output'
CHAR = 'Character'

TEXT_TOKENS = [N, STEP, STOP, GO, TO, SWAP, WITH, OUTPUT, CHAR]

# Tokenize one line of the program listing.
# Returns a (possibly empty) list of tokens or False if an error occurs
def tokenize(line, linenum):
    tokens = []
    curtok = ""
    # split line at whitespace and special characters
    for c in line:
        if c.isspace():
            if curtok == "":
                # discard extra whitespace and continue
                continue
            else:
                # end of current token
                tokens.append(curtok)
                curtok = ""
        elif c == '#':
            if tokens == [] and curtok == "":
                # comment line: ignore the rest of the line
                return tokens
            else:
                printerr("Comment started after non-whitespace character", line, str(linenum))
                return False
        elif c == '.' or c == '+' or c == 'n' or c == 'N':
            if curtok != "":
                # end of current token
                tokens.append(curtok)
            tokens.append(c)
            curtok = ""
        else:
            # add to current token
            curtok += c
    if curtok != "":
        tokens.append(curtok)

    # identify keywords and numbers
    for i in xrange(len(tokens)):
        if tokens[i].isdigit():
            # convert number string to an integer
            tokens[i] = int(tokens[i])
        elif tokens[i] == DOT or tokens[i] == PLUS:
            continue
        else:
            matched = False
            # normalize the capitalization of keywords
            tok = tokens[i].title()
            for validtok in TEXT_TOKENS:
                if tok == validtok:
                    tokens[i] = validtok
                    matched = True
                    break
            if not matched:
                # TODO? The specification says that
                # "Whitespace is allowed before and after tokens".
                # Do we need to allow for the possibility that
                # there may not be any whitespace between keywords
                # or keywords & numbers. (Eg. "Gotostep", "Step10")
                printerr("Ilegal token '" + tokens[i] + "'", line, str(linenum))
                return False
    
    return tokens

# Program data structure
#
# A program is a tuple (numbered steps, expression steps) where the numbered steps
# are stored in a dictionary and the expression steps in a list.  Each numbered
# step is an entry in the dictionary of the form
#           step# -> (instruction code, arg1, arg2)
#
# A STOP instruction takes no arguments:    (iSTOP, None, None)
# A GOTO instruction takes one argument:    (iGOTO, step#, None)
# A SWAP instruction takes two arguments:   (iSWAP, step#, step#)
# An OUTPUT instruction takes one argument: (iOUTP, number, None)
#
# Steps with expressions are stored in a list in the reverse order that they appear
# in the program listing.  Each "n"-expression, an + b, is stored as a tuple (a, b).
# An expression step is a pair with the structure
#           ( (a,b), (instruction code, arg1, arg2) )
# If an argument is a number then it is just an integer element of the inner tuple.
# If an argument is an expression then it is a pair (a,b) as above.  Otherwise an
# argument is 'None'.

# Instruction codes
iSTOP = 0
iGOTO = 1
iSWAP = 2
iOUTP = 3

# Tuple indices

# for program
NUMDSTEPS = 0
EXPRSTEPS = 1

# for "n-"expression steps
NEXPR = 0
NINSTR = 1

# for instructions
ICODE = 0
ARG1 = 1
ARG2 = 2

# Parse an expression which can be just a number or an "n"-expression.
# Returns a pair (result, new idx) where result is an integer, a pair (a,b)
# representing an "n"-expression, or False if an error occurred.  New idx is the
# index of the next token in tokens after the parsed expression.
def parse_expr(tokens, idx, curstep, stepidx):
    leadingnum = None
    haveN = False
    addend = None
    if type(tokens[idx]) is int:
        leadingnum = tokens[idx]
        idx += 1
    if tokens[idx] == N:
        haveN = True
        idx += 1
        if tokens[idx] == PLUS:
            if type(tokens[idx+1]) is int:
                addend = tokens[idx+1]
                idx +=2
            else:
                parsererr("Illegal expression - expected a number after '+'", curstep, tokens, stepidx)
                return (False, idx)
        else:
            addend = 0
    elif leadingnum == None:
        parsererr("Illegal expression - expected a number or 'n'", curstep, tokens, stepidx)
        return (False, idx)

    # have a valid expression, so return the result
    if haveN:
        if leadingnum is None:  leadingnum = 1
        return ((leadingnum, addend), idx)
    else:
        return (leadingnum, idx)

# parse() checks the syntax of the list of tokens and converts them to a "program"
# data structure for the interpreter.  Returns the program or False if an error occurs.
def parse(tokens):
    numberedsteps = {}
    exprsteps = []
    curstep = 0
    curinstr = None
    idx = 0
    endidx = len(tokens)
    while idx < endidx:
        try:
            # beginning of a step definition
            stepidx = idx
            if tokens[idx] == STEP:
                idx += 1
                # parse step number/expression
                (expr,idx) = parse_expr(tokens, idx, curstep, stepidx)
                if type(expr) is bool and not expr:  return False
                if type(expr) is int and expr == 0:
                    parsererr("0 is not a valid step number", 0, tokens, stepidx)
                    return False
                curstep = expr
                if tokens[idx] != DOT:
                    parsererr("Missing '.' after the step number", curstep, tokens, stepidx)
                    return False
                idx += 1
            else:
                parsererr("Missing 'Step' at the beginning of a step definition", curstep, tokens, stepidx)
                return False
            
            # parse step instruction
            # STOP instruction
            if tokens[idx] == STOP:
                idx += 1
                curinstr = (iSTOP, None, None)
            
            # GO TO instruction
            elif tokens[idx] == GO:
                if tokens[idx+1] != TO:
                    parsererr("Missing 'To' after 'Go'", curstep, tokens, stepidx)
                    return False
                if tokens[idx+2] != STEP:
                    parsererr("Missing 'Step' after 'Go To'", curstep, tokens, stepidx)
                    return False
                idx += 3
                # parse target step number/expression
                (expr,idx) = parse_expr(tokens, idx, curstep, stepidx)
                if type(expr) is bool and not expr:  return False
                if type(expr) is int and expr == 0:
                    parsererr("0 is not a valid target step number", curstep, tokens, stepidx)
                    return False
                if type(curstep) is int and not type(expr) is int:
                    parsererr("Illegal 'n'-expression in a numbered step", curstep, tokens, stepidx)
                    return False
                curinstr = (iGOTO, expr, None)
            
            # SWAP instruction
            elif tokens[idx] == SWAP:
                if tokens[idx+1] != STEP:
                    parsererr("Missing 'Step' after 'Swap'", curstep, tokens, stepidx)
                    return False
                idx += 2
                # parse first target step number/expression
                (arg1,idx) = parse_expr(tokens, idx, curstep, stepidx)
                if type(arg1) is bool and not arg1:  return False
                if type(arg1) is int and arg1 == 0:
                    parsererr("0 is not a valid target step number", curstep, tokens, stepidx)
                    return False
                if type(curstep) is int and not type(arg1) is int:
                    parsererr("Illegal 'n'-expression in a numbered step", curstep, tokens, stepidx)
                    return False
                # check for "with step"
                if tokens[idx] != WITH:
                    parsererr("Missing 'With' after first swap target", curstep, tokens, stepidx)
                    return False
                if tokens[idx+1] != STEP:
                    parsererr("Missing 'Step' after 'With'", curstep, tokens, stepidx)
                    return False
                idx += 2
                # parse second target step number/expression
                (arg2,idx) = parse_expr(tokens, idx, curstep, stepidx)
                if type(arg2) is bool and not arg2:  return False
                if type(arg2) is int and arg2 == 0:
                    parsererr("0 is not a valid target step number", curstep, tokens, stepidx)
                    return False
                if type(curstep) is int and not type(arg2) is int:
                    parsererr("Illegal 'n'-expression in a numbered step", curstep, tokens, stepidx)
                    return False
                curinstr = (iSWAP, arg1, arg2)
            
            # OUTPUT instruction
            elif tokens[idx] == OUTPUT:
                if tokens[idx+1] != CHAR:
                    parsererr("Missing 'Character' after 'Output'", curstep, tokens, stepidx)
                    return False
                idx += 2
                # parse number/expression to output
                (expr,idx) = parse_expr(tokens, idx, curstep, stepidx)
                if type(expr) is bool and not expr:  return False
                if type(curstep) is int and not type(expr) is int:
                    parsererr("Illegal 'n'-expression in a numbered step", curstep, tokens, stepidx)
                    return False
                curinstr = (iOUTP, expr, None)
            
            else:
                parsererr("Illegal instruction '" + str(tokens[idx]) + "'", curstep, tokens, stepidx)
                return False
            
            # check for end of step
            if tokens[idx] != DOT:
                parsererr("Missing '.' at end of instruction", curstep, tokens, stepidx)
                return False
            idx += 1
            # add step to program
            if type(curstep) is int:
                numberedsteps[curstep] = curinstr
            else:
                exprsteps.append( (curstep, curinstr) )
                # If this expression can match any previously defined steps, remove them.
                # (We could remove matching expression steps too, but leaving them does
                # not affect the correct execution of the program).
                for stepnum in numberedsteps.keys():
                    if matchNexpression(stepnum, curstep):
                        del numberedsteps[stepnum]
                        warning("Step " + nexpr2str(curstep) + " has replaced step " + str(stepnum))
        except IndexError:
            parsererr("Unexpected end of program OR internal parser error", curstep, tokens, stepidx)
            return False
    
    # reverse the order of the steps with expressions so that the last matching expression has precedence 
    exprsteps.reverse()
    
    return (numberedsteps, exprsteps)

# Converts an "n"-expression tuple (a, b) into the string "an + b".
def nexpr2str(nexpr):
    if nexpr[1] == 0 and nexpr[0] == 1:  return "n"
    elif nexpr[1] == 0:  return "%dn" % nexpr[0]
    elif nexpr[0] == 1:  return "n + %d" % nexpr[1]
    else:  return "%dn + %d" % nexpr

# Convert any expression to a string.
def expr2str(expr):
    if isNexpr(expr):
        return nexpr2str(expr)
    else:
        return str(expr)

# Returns true if stepnum matches the "n"-expression an + b for some positive n.
def matchNexpression(stepnum, nexpr):
    #  check whether an integer n exists that satisfies the equation an + b = stepnum
    an = stepnum - nexpr[1]
    (n, rem) = divmod(an, nexpr[0])
    return rem == 0 and n > 0

# Returns true if arg is a pair (a, b) representing an "n"-expression
def isNexpr(arg):
    return type(arg) is tuple and len(arg) == 2

# Searches a program for a step matching stepnum.  Returns a pair (stepnum, instruction)
# if a match is found.  Returns None if no match found.
def findstep(stepnum, program):
    # look first for stepnum among the numbered steps
    if program[NUMDSTEPS].has_key(stepnum):
        return (stepnum, program[NUMDSTEPS][stepnum])
    else:
        # search for a matching expression step
        for step in program[EXPRSTEPS]:
            if matchNexpression(stepnum, step[NEXPR]):
                return step
    
    # no match found
    return None

# Evaluate any expressions in the instruction portion of an expression step
# and return the new instruction tuple.  Assumes that stepexpr has already
# been checked to match curstepnum.
def evalexprstep(curstepnum, stepexpr, instr):
    #  solve the equation an + b = curstepnum for n
    an = curstepnum - stepexpr[1]
    n = an // stepexpr[0]
    # evaluate the arguments of instr
    if isNexpr(instr[ARG1]):
        arg1 = instr[ARG1][0] * n + instr[ARG1][1]
    else:
        arg1 = instr[ARG1]
    if isNexpr(instr[ARG2]):
        arg2 = instr[ARG2][0] * n + instr[ARG2][1]
    else:
        arg2 = instr[ARG2]

    return (instr[ICODE], arg1, arg2)

# Takes the result of findstep() as input 'step' plus the current step number
# and makes sure that it is ready to be executed or swapped.
def preparestep(step, curstep):
    if step:
        (stepnum, instr) = step
        if isNexpr(stepnum):
            instr = evalexprstep(curstep, stepnum, instr)
    else:
        # no step was found, so use the default STOP instruction
        (stepnum, instr) = (curstep, (iSTOP, None, None))

    # NOTE: stepnum may be an "n"-expression
    return (stepnum, instr)

# Output formats
outINTEGER = 1
outASCII = 2
outUNICODE = 3

def execute(program, outformat = outINTEGER, startstep = 1, trace = False):
    steps = program[NUMDSTEPS]     # dictionary of numbered steps
    # exprsteps = program[EXPRSTEPS] # list of expression steps
    curstep = startstep
    done = False
    while not done:
        step = findstep(curstep, program)
        (stepnum, instr) = preparestep(step, curstep)
        if trace:
            print STEP, curstep,
            printinstruction(instr)
        
        # execute the current step
        instrcode = instr[ICODE]
        if instr[ICODE] == iSTOP:
            done = True
        
        elif instr[ICODE] == iGOTO:
            curstep = instr[ARG1]
        
        elif instr[ICODE] == iSWAP:
            # get the target steps
            target1 = instr[ARG1]
            target2 = instr[ARG2]
            (stepnum1, instr1) = preparestep(findstep(target1, program), target1)
            (stepnum2, instr2) = preparestep(findstep(target2, program), target2)
            # swap them in the program's numbered steps
            steps[target1] = instr2
            steps[target2] = instr1
            curstep += 1
        
        elif instr[ICODE] == iOUTP:
            if outformat == outINTEGER:
                print instr[ARG1]
            elif outformat == outASCII:
                if instr[ARG1] >= 0 and instr[ARG1] <= 127:
                    sys.stdout.write(chr(instr[ARG1]))
                else:
                    warning("ASCII char value %d out of range." % instr[ARG1])
            elif outformat == outUNICODE:
                if instr[ARG1] >= 0 and instr[ARG1] <= 65534:
                    sys.stdout.write(unichr(instr[ARG1]))
                else:
                    warning("Unicode char value %d out of range." % instr[ARG1])
            curstep += 1
        
    return curstep

# Expects a tuple of the form (instruction code, arg1, arg2)
def printinstruction(instr):
    if instr[ICODE] == iSTOP:
        print STOP
    elif instr[ICODE] == iGOTO:
        print GO, TO, instr[ARG1]
    elif instr[ICODE] == iSWAP:
        print SWAP, instr[ARG1], instr[ARG2]
    elif instr[ICODE] == iOUTP:
        print OUTPUT, instr[ARG1]

# MAIN program

# Exit constants
EXIT_OK = 0
EXIT_TOKEN_ERR = 3
EXIT_PARSE_ERR = 4

# set up commandline argument handling
parser = argparse.ArgumentParser(description="An interpreter for the language SMETANA To Infinity!")
parser.add_argument("program", help="filename of the STI program to run")
parser.add_argument("-s", "--start", help="begin execution with step N", type=int, default=1, metavar='N')
parser.add_argument("-t", "--trace", help="trace program execution", action="store_true")
outgrp = parser.add_argument_group("output options", "Set the behavior of the 'Output character' statement.")
outgrp.add_argument("-a", "--ascii", help="output ASCII characters", dest='outformat', action='store_const', const=outASCII, default=outINTEGER)
outgrp.add_argument("-i", "--integers", help="output integers (default)", dest='outformat', action='store_const', const=outINTEGER, default=outINTEGER)
outgrp.add_argument("-u", "--unicode", help="output Unicode characters", dest='outformat', action='store_const', const=outUNICODE, default=outINTEGER)
args = parser.parse_args()

# read program file and tokenize it one line at a time
f = open(args.program)
try:
    linenum = 1
    alltokens = []
    for line in f:
        tokens = tokenize(line, linenum)
        if not tokens and type(tokens) is bool:
            sys.exit(EXIT_TOKEN_ERR)
        # print tokens
        # The spec does not restrict where newlines can appear so we allow
        # steps to cross line boundaries and multiple steps per line.
        # (This contrasts with the SMETANA grammar which requires a newline
        #  after each step).
        alltokens += tokens
        linenum += 1
finally:
    f.close()

# parse tokens and "compile" program
program = parse(alltokens)
if not program and type(program) is bool:
    sys.stderr.flush()
    sys.exit(EXIT_PARSE_ERR)
# print program

# run the program with the specified options
execute(program, args.outformat, args.start, args.trace)
sys.exit(EXIT_OK)
