import os
import sys

class shreddable():

#Variables-------------------------------------------
    filename = ""
    directory = False
    iterations = 3
    zero = False
    remove = False

#Member functions-------------------------------------
    def shred(self):
        command = "shred " + "-n" + str(self.iterations)
        if(self.zero == True):
            command += " -z"
        if(self.remove == True):
            command += " -u"
        command += " " + self.filename
        os.system(command)

    def rshred(self):
        command = "find " + self.filename + " -type f -exec shred -n" + str(self.iterations)
        if(self.zero == True):
            command += " -z"
    
        command += " '{}' \;"
        os.system(command)

        if(self.remove == True):
            removedir = "rm -r " + self.filename
            os.system(removedir)

    def destroy(self):
        if(os.path.exists(self.filename) != True):
            sys.exit("ERROR: filename does not exist-developers-check implementation of filename section")

        if(os.path.isdir(self.filename) == True):
            self.rshred()

        else:
            self.shred()






        
    


