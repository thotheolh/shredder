#!/usr/bin/python
import os
def shred(filename, iterations):
	#shredding function
	command = "shred " + "-n" + iterations + " " + filename
	os.system(command)

filename = raw_input("Enter file to shred:	")
iterations = raw_input("Iterations:	")
#shred call
shred(filename, iterations)
