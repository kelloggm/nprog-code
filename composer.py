#!/usr/bin/python

import sys
import getopt
import random
import subprocess

class Cluster(object):
	def __init__(self, edit_list, output_file, cluster_size, glob_size, gpath, config, replacement, budget, seed):
		self.edit_list = edit_list
		self.output_file = output_file
		self.n = cluster_size
		self.k = glob_size
		self.seed = seed
		self.gpath = gpath
		self.config = config
		self.replacement = replacement
		self.y = budget
		self.check_config()
		self.write_parameters()
		self.generate_cluster()

	def check_config(self):
		with open(self.config, "r") as a:
			config_lines = a.readlines()
		with open(self.config, "w") as b:
			for line in config_lines:
				if "--oracle-genome" not in line and "--no-test-cache" not in line and "--no-rep-cache" not in line and line.strip():
					b.write(line)

	def write_parameters(self):
		with open(self.output_file, "w") as f:
			parameters = [
				"number of edits in list : " + str(len(self.edit_list)),
				"number of globs (n) : " + str(self.n),
				"size of globs (k) : " + str(self.k),
				"replacement : " + str(self.replacement),
				"path to GenProg : " + self.gpath,
				"configuration file : " + self.config ]
			for entry in parameters:
				f.write(entry + '\n')

	def generate_cluster(self):
		for i in range(self.n):
			g = Glob(self.edit_list, self.output_file, self.k, self.gpath, self.config, self.replacement, self.seed)
			count = 0
			while not g.is_neutral(i) and count < self.y:
				g = Glob(self.edit_list, self.output_file, self.k, self.gpath, self.config, self.replacement, self.seed)
				count += 1
			if count == self.y:
				assert self.k > 1, "k has decreased to 1, so we're doing nothing"
				with open(self.output_file, "a") as f:
					f.write("tried %d without a neutral varient: dropping k from %d to %d\n" % (self.y, self.k, int(self.k / 2.0)))
				self.k = int(self.k / 2.0)

class Glob(object):
	def __init__(self, edit_list, output_file, glob_size, gpath, config, replacement, seed):
		random.shuffle(edit_list)
		self.edit_list = edit_list
		self.output_file = output_file
		self.k = glob_size
		self.gpath = gpath
		self.config = config
		self.replacement = replacement
		self.seed = seed
		self.glob = []
		self.edited_lines = []
		self.make_glob()
	
	def test_edited_lines(self, edit):
		for line in edit.translate(None, "ad()").split(','):
			if line in self.edited_lines:
				return False
		for line in edit.translate(None, "ad()").split(','):
			self.edited_lines.append(line)
		return True

	def make_glob(self):
		i = 0
		j = 0
		while len(self.glob) < self.k and i < len(self.edit_list):
			ok = self.test_edited_lines(self.edit_list[i])
			if ok:
				self.glob.append(self.edit_list[i])
				j += 1
			i += 1
	
	def get_glob_str(self):
		result = ""
		for line in self.glob:
			result += " " + line
		return result.strip()

	def is_neutral(self, i):
		glob_str = self.get_glob_str()
		subprocess.call([self.gpath, self.config, "--oracle-genome", glob_str])
		with open("repair.debug." + self.seed, "r") as f:
			for line in f:
				if "was neutral" in line and "cil" not in line:
					with open(self.output_file, "a") as a:
						a.write(line)
					subprocess.call("mkdir n-prog-output/cluster-" + str(i), shell=True)
					subprocess.call("mv 000000* n-prog-output/cluster-"+str(i)+"/", shell=True)
					return True
				if "was not neutral" in line and "cil" not in line:
					with open(self.output_file, "a") as b:
						b.write(line)
					return False
		raise Exception("Did not find line of interest in repair.debug.0")

def read_input_file(input_file):
	edit_list = []
	with open(input_file, "r") as f:
		for line in f:
			edits = line.split()
			for edit in edits:
				if edit not in edit_list:
					edit_list.append(edit)
	return edit_list

def usage():
	print "[-h,--help] (displays this help message, then exits)"
	print "[-i,--input-file] file name (defaults to 'genomes')"
	print "[-o,--output-file] file name (defaults to 'composer_output')"
	print "[-n,--num-globs] integer (defaults to 8)"
	print "[-k,--glob-size] integer (defaults to 30)"
	print "[-g,--genprog-path] relative path to GenProg (required)"
	print "[-c,--configuration-file] file name (defaults to 'configuration')"
	print "[-r,--replacement-off] (replacement is on by default)"
	print "[-y,--search-budget] how many probes before reducing k (defaults to 50)"
	print "[-s,--seed] random seed"

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:o:n:k:g:c:ry:s:", ["help", "input-file=", "output-file=", "num-globs=", "glob-size=", "genprog-path=", "configuration-file=", "replacement-off", "search-budget=", "seed="])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	# defining defaults for most options
	input_file = "genomes"
	output_file = "composer_output"
	n = 8 # number of globs in cluster
	k = 30 # size of each glob
	config = "configuration"
	replacement = True
	gpath = None # required option
	y = 50 # number of probes before giving up and reducing k
	for opt,arg in opts:
		if opt in ["-h","--help"]:
			usage()
			sys.exit(2)
		elif opt in ["-i","--input-file"]:
			input_file = arg
		elif opt in ["-o","--output-file"]:
			output_file = arg
		elif opt in ["-n","--num-globs"]:
			n = int(arg)
		elif opt in ["-k","--glob-size"]:
			k = int(arg)
		elif opt in ["-g","--genprog-path"]:
			gpath = arg
		elif opt in ["-c","--configuration-file"]:
			config = arg
		elif opt in ["-r","--replacement-off"]:
			replacement = False
		elif opt in ["-y","--search-budget"]:
			y = int(arg)
		elif opt in ["-s","--seed"]:
			seed = arg
			random.seed(arg)

	if gpath is None:
		usage()
		sys.exit(2)

	edit_list = read_input_file(input_file)
	if len(edit_list) < k:
		k = int(len(edit_list)/4.0*3.0)
	Cluster(edit_list, output_file, n, k, gpath, config, replacement, y, seed)
	subprocess.call("cp " + output_file + " n-prog-output/composer_output", shell=True)

if __name__ == "__main__":
	main(sys.argv[1:])
