@ Martin Kellogg
updated 10/21/2015

#####################################
Overview
#####################################

This file describes a research protoype implementation of the N-Prog system for proactive diversity. N-Prog creates several different variants of a target program for use in an n-variant system to detect defects or attacks. For more details of the N-Prog algorithm, see "N-Prog: A Framework for Proactive, Coarse-grained Diversity," by Kellogg et al. (forthcoming?)

To use N-Prog, one needs a few things already in hand:
   1. A working version of GenProg (http://dijkstra.cs.virginia.edu/genprog/); N-Prog requires revision 1613 or later to work correctly; the experiments in the paper use revision 1681.
   2. A version of the program you wish to protect which has been instrumented for use with GenProg. See the GenProg documentation for information on how to instrument a program correctly.
      N-Prog needs the main configuration file to be named "configuration-default"; it will automatically create the configuration files it will actually use based on this file.
      Note that N-Prog will override some of the configuration flags in the configuration-default file - especially the seed, search strategy, and number of negative tests.
   3. The files accompanying this README
   4. Coverage information. If you have coverage information available already in GenProg's format (i.e. the same format as "coverage.path.pos" or similarly named GenProg files), rename it to "pd-weight" so that N-Prog can find it. Otherwise, N-Prog will invoke GenProg's coverage utility (so if you don't have coverage information and you're working with a C program, you can ignore this).


Once these have been gathered, N-Prog can be run on (2) by running the "n-prog" script accompanying this README. This script requires several arguments. Here is an example command:
     ./n-prog -d ~/home/weimer/gcd/ -r ~/repair -n 4 -k 10

     The -d flag tells N-Prog the directory containing the instrumented program to diversify. This option is required.
     The -r flag tells N-Prog where to find the GenProg executable to use when searching for neutral edits. If no -r option is specified, it tries ~/repair
     	    Note: If you want to supply a relative path here, it has to be relative to the directory supplied to -d (sorry...I'll try to fix this in the future)
     The -n flag tells N-Prog how many variants of the original program to create. If no option is specified, N-Prog will use n=8.
     The -k flag tells N-Prog the maximum number of edits allowed in each variant. We find that k=30 (the default) is a good choice empirically for most programs.
     The -x flag specifies the variant search budget for N-Prog; i.e. how many individual neutral edits N-Prog tries. This defaults to x=400.
     The -y flag specifies the cluster search budget for N-Prog. The default is y=50.
     The -s flag specifies the random seed to use. Defaults to 0.
     The -f flag can be used to specify a fault scheme to genprog. This should only be used if you know how genprog works internally - this flag is passed directly to genprog.
    
N-Prog produces a number of clusters, which are found in the directory supplied to -d as C source files in the "n-prog-output" directory.

This repository also contains a file called "clean.sh".  This script can be run to remove the files created by N-Prog and GenProg after they are run in a directory.

#####################################
The Look Example
#####################################

N-Prog also includes an example scenario so that you can check if your setup is working correctly. This example scenario protects look, 
a UNIX utility for checking the spelling of words (not the most exciting example, but it's a simple program). In the text that follows,
bash commands are proceeded by a ">"
     > echo "like this"
while English descriptive text appears normally.

If you untar the look-example.tar.gz file
     > tar xf look-example.tar.gz
you will create a "look-example" directory. This directory contains the look example. It also includes a README that describes
the function of each of the files that were included in that directory.

You also need a working version of GenProg. Included in the look example is the binary for GenProg version 1681, which was 
used in the N-Prog paper for all of its experiments. That binary may not work on all systems; if it does not work on yours,
substitute your own by compiling GenProg.

From the n-prog-code directory, run the following command:
     > ./n-prog -d ~/n-prog-code/look-example -r ~/n-prog-code/look-example/repair -n 25

Note that the pathnames passed to N-Prog MUST BE ABSOLUTE PATHS

On my local system, that commands takes about five minutes to run. It will create a large number of variants (informing you
of its progress along the way), and then combine them.

Once it finishes, move into the look-example directory. There should now be a "n-prog-output" directory. Switch to that directory and look around.
     > cd look-example/n-prog-output; ls

You should see 25 directories labeled "cluster-i" where i is a number between 0 and 24, inclusive. Each of these directories contains the source
code and an executable for that particular cluster. You should also see a file called "composer_output". That file contains a summary of the results
of the composition step. Notably, it also contains information about which of the created variants pass held-out negative tests (in the example, this is
none of the clusters :( ). The look-example directory also contains the version of this file that I generated when I ran the example. It is "composer_output_expected",
and you can check to see if your run went as expected by diffing the resulting composer_output file with this file.
    > diff composer_output ../composer_output_expected

The test suite provided with the look example is relatively weak; if we manually inspect the 25 clusters, it turns out that many of them actually
have behavior that's very incorrect. Try to find one with behavior that you don't expect on some simple test case you come up with (basically, pick
the first word that comes to mind!).

If you can't think of a good word to test with, "genetic" worked well for us.

The look example also includes a script which can be used to run all the clusters on a given input. This isn't a real deployment script;
rather, it's a way to simulate deploying all the clusters. It will report back the results of running each cluster on the given input,
and indicate a divergence if one exists. If there's no divergence, it will print "no divergence".

It takes the name of the directory that holds all the clusters as its first input, and the test case you'd like to run as the second.

Here's how to run it:
       > ./look-runner.sh ~/n-prog-code/look-example/n-prog-output "genetic"

With high probability, you'll discover that at least one of the clusters you generated does diverge on the input you use --- and it probably
shouldn't. So, we need to add a test case. Doing so is a bit more involved than the rest of the tutorial, so if you feel like you understand
how N-Prog works at this point, now is a good time to stop.

In the following, I'm going to assume that your test input is the word "genetic"; if you want to use something else, that's fine (even encouraged),
but you'll have to replace every instance of "genetic" in the following with your test input.

In the test.sh file, there's already code for a 15th positive test: it's found under "p15." Basically, it runs the program with the input found in
the "tp9" file and compares the output to what's found in the "out.8" file (the numbers are just based on how many of those kinds of file already
exist in the directory and are otherwise meaningless). Both "tp9" and "out.8" exist but are empty; you'll need to modify them. "tp9" is easier; it should
contain the test input and nothing else. For us, "cat tp9" prints just "genetic". "out.8" needs to hold the correct output. In practice, we would require
an oracle for this --- usually developers. However, most UNIX systems have look installed, and we can use that (known-correct) version as our oracle. 
To produce our version of "out.8", we used the following command:
   > look "genetic" > out.8

Once both of these files have the correct contents, we need to tell N-Prog to use all 15 tests. This can be accomplished by editing the "configuration-default"
file. In that file, you'll find a line like this:
      --pos-tests 14

This line tells N-Prog how many positive tests the program has. We need to change that to 15, instead of 14. The result should look like this:
     --pos-tests 15

Finally, we need to clear the coverage cache (which is dependent on the number of test cases but doesn't clear automatically). We can do that by deleting
the "pd-weight" file:
    > rm -f pd-weight

Once that's done, we need to generate new clusters; we'll rerun N-Prog exactly the same way we did earlier. Then, we can retest the resulting clusters. If they
still are not good, we can add additional tests. Repeating this process shows the expected deployment scenario for N-Prog.
