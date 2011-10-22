#!/usr/bin/python
import os
def shred(filename):
	os.system(filename)

filename = "shred "
filename += raw_input("Enter file to shred")

shred(filename)
