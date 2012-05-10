#!/usr/bin/env python

import os

## File I/O for Properties file.
## Each line of file would contain a property key/value.
## e.g. xxx_key=yyy_val

class properties():

    props = [] #Array for properties
    file = None

    ## Constructor.
    def __init__(self, properties_file):
        self.propsLoc = properties_file
        self.read()

    ## To be called to read and parse properties file before doing anything else.   
    def read(self):
        if os.path.exists(self.propsLoc):
            self.file = open(self.propsLoc,"r+")
            for line in self.file:
                self.translate(line)
        else:
            self.file = open(self.propsLoc,"w+")

    ## Write the properties into the file.
    def write(self, key_value_list):
        if(isinstance(key_value_list, list)): #Checks if key_value_list is a list, else do nothing.
            self.file = open(self.propsLoc,"w+")
            for i in range (0, len(key_value_list)):
                element = key_value_list[i]
                self.file.write(str(element[0])+"="+str(element[1])+"\n")

    ## Close file.
    def close(self):
        self.file.close()

    ## Size of properties.
    def size(self):
        return len(self.props)

    ## Get property at i.
    def get(self, i):
        return self.props[i]

    ## Gets the entire properties list.
    def get_props_list(self):
        return self.props

    ## Remove properties that fits an exact list.
    def remove(self, key_value_list):
        if(isinstance(key_value_list, list)):
            self.props.remove(key_value_list)
            return True
        else:
            return False
    
    ## Resets all properties. No more properties.
    def reset(self):
        self.props = []
        if self.size() == 0:
            return True
        else:
            return False

    ## Takes in a line of the file input and parses it for properties.
    def translate(self, line):
        str = line.split("=")
        if len(str) > 1:
            str[1] = str[1].rstrip("\n")
            self.props.append([str[0], str[1]])
