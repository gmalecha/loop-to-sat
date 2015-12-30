Loop To SAT
===========

This program solves puzzles in the [loop game](https://play.google.com/store/apps/details?id=com.balysv.loop) by converting them to SAT formulas.


Requirements
------------

This program requires that a recent version of [z3](https://github.com/Z3Prover/z3) be available on your path.

Usage
-----

The common usage is the following

   python loop.py <file>

where <file> is the path to the file that contains the board (see the next
section for the format of the file). If the board is to be specified via
standard input, the -in flag can be passed. The SAT problem can be printed
to standard error by passing the --dump flag.

Board Format
------------

The format of the board is a single file with one line per row of the board.
The following characters are used to encode the number of outputs of each cell
in the board.

   - `0` a blank square
   - `1` a square with one output
   - `|` a square with two outputs on opposite sides
   - `L` a square with two adjacent outputs
   - `T` a square with three outputs
   - `+` a square with four outputs