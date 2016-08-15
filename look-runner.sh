#!/bin/bash

CLUSTER_DIR=$1
TEST=$2

pushd $CLUSTER_DIR/..  &> /dev/null
gcc -o look look.c &> /dev/null
cp look $CLUSTER_DIR
cp words $CLUSTER_DIR
popd &> /dev/null
pushd $CLUSTER_DIR  &> /dev/null
./look < $TEST &> orig-output
popd &> /dev/null

FNDIVERGE=1

for i in $CLUSTER_DIR/cluster*; do
    cp $CLUSTER_DIR/../words $i
    pushd $i &> /dev/null
    ./000000 < $TEST &> out
#    cat out
    if diff out $CLUSTER_DIR/orig-output &> /dev/null; then
	:
    else
	FNDIVERGE=0
	echo "$i diverges"
    fi
    rm out
    popd &> /dev/null
done

if [[ $FNDIVERGE -eq 1 ]]; then
    echo "no divergence"
fi
