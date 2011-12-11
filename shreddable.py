import os
import sys

class shreddable():

#Variables-------------------------------------------
    filename = ""
    directory = False
    iterations = 3
    zero = False
    remove = False
    gui = None

#Member functions-------------------------------------
    def shred(self):
        command = "shred " + "-n" + str(self.iterations)
        if (self.zero == True):
            command += " -z"
        if (self.remove == True):
            command += " -u"
        command += " \"" + self.filename + "\""

        ## Check if GUI parameter is passed over. If GUI parameter is found, proceed to divert output to GUI output.
        if (self.gui != None):

           # Displays on the GUI output console the files that are being shredded at the moment
           self.gui.insertText("Shredding: "+self.filename+"\n")

        os.system(command)

    def rshred(self):
        command = "find \"" + self.filename + "\" -type f -exec shred -n" + str(self.iterations)
        if (self.zero == True):
            command += " -z"
    
        command += " '{}' \;"
        os.system(command)

        if (self.remove == True):
            removedir = "rm -r \"" + self.filename + "\""
            os.system(removedir)

    def destroy(self):
        if (os.path.exists(self.filename) != True):

            ## Check if GUI parameter is passed over. If GUI parameter is found, proceed to divert output to GUI output.
            if (self.gui != None):

                # Displays on the GUI output console the files that are being shredded at the moment
                self.gui.insertText("Warning! - "+self.filename+" does NOT EXIST! An implementation bug on the filename section has occurred !\n")
            else:
                sys.exit("ERROR: filename does not exist-developers-check implementation of filename section")

        if (os.path.isdir(self.filename) == True):
            self.rshred()

        else:
            self.shred()






        
    


