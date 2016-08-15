#!/usr/bin/python

# @ Martin Kellogg ; May 2015

# This script takes a genprog configuration file for an existing benchmark program and converts it into a form usable by the proactive diversity scripts

import sys

config_file = sys.argv[1]
seed = sys.argv[2]
fault_scheme = sys.argv[3]

mpOverwrite = {"--search" : "pd-explore", "--promut" : "1", "--seed" : seed, "--popsize" : "400", "--describe-machine" : "", "--fix-scheme" : "uniform", "--fault-scheme" : fault_scheme, "--fault-file" : "pd-weight", "--pd-mutp" : "0", "--ignore-dead-code":"", "--ignore-standard-headers":"", "--ignore-string-equiv-fixes":"", "--ignore-equiv-appends":"", "--ignore-untyped-returns":"", "--swapp" : "0", "--skip-failed-sanity-tests":"", "--sanity":"yes"}

for ln in open(config_file):
    ln = ln.strip()
    if ln is "":
        continue
    option = ln.split()[0]
    if option in mpOverwrite:
        print option + " " + mpOverwrite[option]
        del mpOverwrite[option]
    else:
        print ln

for option in mpOverwrite.keys():
    print option + " " + mpOverwrite[option]
