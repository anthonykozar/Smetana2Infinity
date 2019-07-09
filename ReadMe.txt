Smetana2Infinity.py
===================

An interpreter for the language "SMETANA To Infinity!".

SMETANA To Infinity! is an esoteric programming language created by Tanner Swett. It was inspired by the language SMETANA by Chris Pressey.

Programs in both languages consist of a list of numbered steps with each step indicating one instruction to be performed.  SMETANA has only two instructions: "Go to step [number]" and "Swap step [number] with step [number]".  SMETANA To Infinity! adds "Stop" and "Output" instructions but more importantly allows step numbers to be expressions of the form "an + b".

Here is a sample SMETANA To Infinity! program:

	Step n. Output character n.
	Step 4. Swap step 1 with step 2.
	Step 5. Swap step 3 with step 7.
	Step 6. Go to step 1.
	Step 7. Stop.

This program will output numbers from 1 to 3 than back to 1 before stopping.  Execution begins with step 1 and any step that does not have an explicit definition in this program will match "Step n". 

More information on the languages SMETANA To Infinity! and SMETANA are available from

http://esolangs.org/wiki/SMETANA_To_Infinity!
https://catseye.tc/article/Automata.md#smetana


The interpreter
---------------

Smetana2Infinity.py is written in Python 2 and tested with Python 2.7.16 on Mac OS X.  It attempts to be faithful to the specification given at esolangs.org without adding any language extensions.  The interpreter is intended to be run from a commandline and has the following usage and options.

Usage: Smetana2Infinity.py [-h] [-s N] [-t] [-a] [-i] [-u] program-file

Optional arguments:

  -h, --help       shows a help message and exits
  -s N, --start N  begin execution with step N
  -t, --trace      trace program execution

The --trace option causes the step number and instruction to be printed for each step executed.  The --start option allows execution to begin with a step other than step 1.  In addition to running only part of a program, this can be useful as a mechanism for passing a single integer input to a program if it is written in an appropriate way.  Try this with either of the Collatz sequence example programs.

Output options:

  -a, --ascii      output ASCII characters
  -i, --integers   output integers (default)
  -u, --unicode    output Unicode characters

These options set the behavior of the 'Output character' statement.  The specification says that "the interpretation of the numbers which are output is unspecified" so this implementation provides three different methods for greater utility.  The "hello.s2i" and "hello2.s2i" examples should be run with the -a or -u option while the default integer output is intended for the Collatz and primes examples.

SMETANA To Infinity! is mostly backwards-compatible with SMETANA, so Smetana2Infinity.py should be able to execute most SMETANA programs as well.


Download and Contact Info
-------------------------

Smetana2Infinity.py was implemented by Anthony Kozar in June and July of 2019 and is available on GitHub.  Please send comments, questions, bugs, and sample programs to the email address on my website.  Thanks!  

https://github.com/anthonykozar/Smetana2Infinity

http://anthonykozar.net/
