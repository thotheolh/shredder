#!/usr/bin/python

#import shredding algorithm:
import os
from Shred import shred
from Recursive import rshred


#shred options input:

#filename of target file here
filename = raw_input("Enter file to shred:	")

#check file exists
while((os.path.exists(filename)) != True):
	print'Error: file \"', filename, '\" does not exist'
	filename = ""
	filename = raw_input("Enter file to shred:	")

#check for directory filename
directory = False
if((os.path.isdir(filename)) == True):
	directory = True
	
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
if(directory == True):
	rshred(filename, iterations, zero, remove)
if(directory == False):
	shred(filename, iterations, zero, remove)
