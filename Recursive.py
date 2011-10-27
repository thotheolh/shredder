#!/usr/bin/python

#####################################################################
#HIGHLY DANGEROUS-DO NOT USE UNLESS YOU ARE CONFIDENT               #
#####################################################################


import os
def rshred(filename, iterations, zero, remove):
	#shredding function:

	#concantenate and parse variables passed
	command = "find " + filename + " -type f -exec shred -n" + iterations
	if(zero == "y"):
		command += " -z"
	command += " '{}' \;"
	
	
	#final system call
	os.system(command)

	#remove directory - "clean up"
	if(remove == "y"):
		removedir = "rm -r " + filename
		os.system(removedir)

