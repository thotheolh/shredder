#!/usr/bin/python
import os
def shred(filename, iterations, zero, remove):
	#shredding function:

	#contancenate and parse variables passed
	command = "shred " + "-n" + iterations
	if(zero == "y"):
		command += " -z"
	if(remove == "y"):
		command += " -u"
	
	#variable to pass to system() call.	
	command += " " + filename

	#final system call
	os.system(command)

