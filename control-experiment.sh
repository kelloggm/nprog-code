#!/bin/bash

# @ Martin Kellogg ; July 2015

# This script is used to run one of the main proactive diversity experiments for Martin and Jamie's summer 2015 project

# $1 should be a path to the repair executable
# $2 and $3 should be n and k

REPAIR=$1
N=$2
K=$3
X=$4
Y=$5
FAULT_SCHEME=$6
SEED=$7

# need to generate configuration files

./configuration-rewriter-pd.py configuration-default $SEED $FAULT_SCHEME > configuration-pd
./configuration-rewriter-cov.py configuration-default $SEED > configuration-cov
./configuration-rewriter-delphi.py configuration-default $SEED > configuration

echo "--popsize $X" >> configuration-pd

if ! [[ -f pd-weight ]]; then
    if ! [[ -f configuration-cov ]]; then
	echo "control-experiment.sh: Cannot compute or find coverage information. Exiting now."
	exit 2
    fi
    rm -rf *coverage*
    $REPAIR configuration-cov
    cp coverage.path.pos pd-weight
    if ! [[ -f pd-weight ]]; then
	echo "control-experiment.sh: An error occurred while computing coverage. Exiting now."
	exit 3
    fi
fi

if ! [[ -d source ]]; then
    mkdir source
fi

mkdir n-prog-output

$REPAIR configuration-pd
grep "passed [0-9]" repair.debug.$SEED | cut -f 1 -d p | sed "s/^..//" > genomes
if ! [[ -d repair.debug ]]; then
    mkdir repair.debug
fi
mv repair.debug.$SEED repair.debug/repair.debug.original
./run_tests.py $REPAIR $N $K $Y $SEED
