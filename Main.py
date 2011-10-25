#!/usr/bin/python

#import shredding algorithm:
import os
from Shred import shred


#shred options input:

#filename of target file here
filename = raw_input("Enter file to shred:	")

#check file exists
while((os.path.isfile(filename)) != True):
	print'Error: file \"', filename, '\" does not exist'
	filename = ""
	filename = raw_input("Enter file to shred:	")

#iterations of shred command
iterations = raw_input("Iterations:	")

#overwrite file with zeros afterwards? <bool variable needed>
zero = raw_input("Zero after shredding? [y/n]")

#check zero input is boolean and expected
while ((zero != "y") and (zero != "n")):
	zero = ""
	zero = raw_input("Zero after shredding? [y/n]")

#remove file after shredding?
remove = raw_input("Remove file after shredding[y/n]")

#check input for accuracy
while ((remove != "y") and (remove != "n")):
	remove = ""
	remove = raw_input("Zero after shredding? [y/n]")

#call to shred function from shred.py
shred(filename, iterations, zero, remove)
