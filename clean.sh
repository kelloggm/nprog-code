#!/bin/bash

# @ Martin Kellogg

# This script removes the files created by running N-Prog and GenProg in a directory. It will not remove the output of N-Prog or coverage information, but will remove all other files.

# It should be run in the directory to be cleaned.

rm -rf source/ sanity/ repair.debug/

rm configuration configuration-pd configuration-cov
rm *.cache
rm repair.*

rm 00*.c
rm 00*

rm composer.py control-experiment.sh run_tests.py configuration-rewriter*
rm repair.debug.*

rm clean.sh