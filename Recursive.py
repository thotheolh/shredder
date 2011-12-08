#!/usr/bin/python

#####################################################################
#HIGHLY DANGEROUS-DO NOT USE UNLESS YOU ARE CONFIDENT               #
#####################################################################


import os
def rshred(file1):

	#check user:
	confirmdir = raw_input("This is a directory-continue? [y/n]")
	while((confirmdir != "y") and (confirmdir != "n")):
		confirmdir = raw_input("This is a directory-continue? [y/n]")
	#shredding function:

	#concantenate and parse variables passed
	command = "find " + file1.filename + " -type f -exec shred -n" + file1.iterations
	if(file1.zero == "y"):
		command += " -z"
	command += " '{}' \;"
	
	
	#final system call
	if(confirmdir == "y"):
		os.system(command)

	#remove directory - "clean up"
	if(file1.remove == "y"):
		removedir = "rm -r " + file1.filename
		os.system(removedir)

