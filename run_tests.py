#!/usr/bin/python

import subprocess
import sys

repair = sys.argv[1]
n = sys.argv[2]
k = sys.argv[3]
y = sys.argv[4]
seed = sys.argv[5]

cluster_sizes = [int(n)]

num_edits = [int(k)]

for i in cluster_sizes:
	for j in num_edits:
		subprocess.call(["./composer.py","-g", repair, "-n", str(i), "-k", str(j), "-o", "output."+str(i)+"."+str(j), "-y", y, "-s", seed])

