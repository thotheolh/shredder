#!/usr/bin/python
import os
def shred(filename, iterations, zero, remove):
	#shredding function
	command = "shred " + "-n" + iterations
	if(zero == "y"):
		command += " -z"
	if(remove == "y"):
		command += " -u"
	command += " " + filename
	os.system(command)



#shred options input
filename = raw_input("Enter file to shred:	")
iterations = raw_input("Iterations:	")
zero = raw_input("Zero after shredding? [y/n]")
while ((zero != "y") and (zero != "n")):
	zero = ""
	zero = raw_input("Zero after shredding? [y/n]")
remove = raw_input("Remove file after shredding[y/n]")
while ((remove != "y") and (remove != "n")):
	remove = ""
	remove = raw_input("Zero after shredding? [y/n]")

#shred call
shred(filename, iterations, zero, remove)
