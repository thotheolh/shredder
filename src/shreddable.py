#!/usr/bin/env python

import os, sys, shutil

class shreddable():

#Constructor-------------------------------------------
    
    def __init__(self, filename, iterations, zero, remove, gui):
		self.filename = filename
		self.iterations = iterations
		self.zero = zero
		self.remove = remove
		self.gui = gui
		

#Member functions-------------------------------------
    def shred(self, filename):
        command = "shred " + "-n" + str(self.iterations)
        if (self.zero == True):
            command += " -z"
        if (self.remove == True):
            command += " -u"
        command += " \"" + filename + "\""

        ## Check if GUI parameter is passed over. If GUI parameter is found, proceed to divert output to GUI output.
        if (self.gui != None):

           # Displays on the GUI output console the files that are being shredded at the moment
           self.gui.insertText(_("Processing file ")+filename+"\n")

        os.system(command)

    def rshred(self):
		for dirname, dirnames, filenames in os.walk(self.filename):
			for filename in filenames:
				self.shred(os.path.join(dirname, filename))
				
		for dirs in os.listdir(self.filename):
			shutil.rmtree(self.filename + "/" + dirs)
	
	

    def destroy(self):
        if (os.path.exists(self.filename) != True):

            ## Check if GUI parameter is passed over. If GUI parameter is found, proceed to divert output to GUI output.
            if (self.gui != None):

                # Displays on the GUI output console the files that are being shredded at the moment
                self.gui.insertText("Warning! - "+self.filename+" does NOT EXIST! Please re-select a valid file.\n")
            else:
                sys.exit("ERROR: filename does not exist-developers-check implementation of filename section")

        if (os.path.isdir(self.filename) == True):
            self.rshred()

        else:
            self.shred(self.filename)






        
    


