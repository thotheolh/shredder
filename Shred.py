#!/usr/bin/python
import os
def shred(file1):
	#shredding function:

	#contancenate and parse variables passed
	command = "shred " + "-n" + file1.iterations
	if(file1.zero == "y"):
		command += " -z"
	if(file1.remove == "y"):
		command += " -u"
	
	#variable to pass to system() call.	
	command += " " + file1.filename

	#final system call
	os.system(command)

