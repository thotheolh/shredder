#!/usr/bin/python

#import shredding algorithm:
import os
from Shred import shred
from Recursive import rshred
from GetFile import GetFile
from target import target


#shred options input:
#new class
file1 = target

#get and parse filename
file1.filename = GetFile()
#check directories
file1.directory = False
if((os.path.isdir(file1.filename)) == True):
	file1.directory = True
	
#iterations of shred command
file1.iterations = raw_input("Iterations:	")

#overwrite file with zeros afterwards? <bool variable needed>
file1.zero = raw_input("Zero after shredding? [y/n]")

#check zero input is boolean and expected
while ((file1.zero != "y") and (file1.zero != "n")):
	file1.zero = ""
	file1.zero = raw_input("Zero after shredding? [y/n]")

#remove file after shredding?
file1.remove = raw_input("Remove file after shredding[y/n]")

#check input for accuracy
while ((file1.remove != "y") and (file1.remove != "n")):
	file1.remove = ""
	file1.remove = raw_input("Zero after shredding? [y/n]")

#call to shred function from shred.py
if(file1.directory == True):
	rshred(file1)
if(file1.directory == False):
	shred(file1)
