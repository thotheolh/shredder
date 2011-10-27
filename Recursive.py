#!/usr/bin/python

#####################################################################
#HIGHLY DANGEROUS-DO NOT USE UNLESS YOU ARE CONFIDENT               #
#####################################################################


import os
def rshred(filename, iterations, zero, remove):

	#check user:
	confirmdir = raw_input("This is a directory-continue? [y/n]")
	while((confirmdir != "y") and (confirmdir != "n")):
		confirmdir = raw_input("This is a directory-continue? [y/n]")
	#shredding function:

	#concantenate and parse variables passed
	command = "find " + filename + " -type f -exec shred -n" + iterations
	if(zero == "y"):
		command += " -z"
	command += " '{}' \;"
	
	
	#final system call
	if(confirmdir == "y"):
		os.system(command)

	#remove directory - "clean up"
	if(remove == "y"):
		removedir = "rm -r " + filename
		os.system(removedir)

