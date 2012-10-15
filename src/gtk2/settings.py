#!/usr/bin/env python

from properties import properties
from util import *
import os

## This class does NOT handle the File I/O of the actual settings. They are to simply handle, hold and translate settings.
class settings():

    version = "1.1 Alpha" #Hard code version.
    iterations = "5"            #Default.
    remove_shredded = False  #Default.
    zero = True              #Default.
    util = util()
    props = None
    props_fname = "system.properties"

    ## Init
    def __init__(self):
        self.get()

    ## Gets settings. Calls I/O to read files settings and load in. Checks if local directory is writable, else use home directory for configs.
    def get(self):
        self.props_file = self.util.get_resource(self.props_fname)
	if not os.access(self.props_file, os.W_OK):
            shome = os.getenv("HOME") + "/.shredder/"
            if not os.path.exists(shome):
                os.makedirs(shome)
            self.props_file = shome + self.props_fname                	    		
        self.props = properties(self.props_file)
        for i in range(0, self.props.size()):
            self.translate(self.props.get(i))            
        self.props.read()
        
    ## Save existing settings. Calls up I/O methods in another class to do the physical saving of settings.
    def commit(self):
        key_value_list = [["shr.iter", int(self.get_shred_iterations())], ["shr.zero", self.is_zero()], ["shr.remove", self.is_remove_shredded()]]
        self.props.write(key_value_list)
        self.get()

    ## Gets version
    def get_version(self):
        return self.version

    ## Get shredding iterations.
    def get_shred_iterations(self):
        return self.iterations

    ## Set shredding iterations.
    def set_shred_iterations(self, iters):
        self.iterations = iters

    ## Check if shredded items are removed.
    def is_remove_shredded(self):
        return self.remove_shredded

    ## Set removal of shredded items.
    def set_remove_shredded(self, to_remove):
        self.remove_shredded = to_remove

    ## Check if shredded items are zeroed.
    def is_zero(self):
        return self.zero

    ## Set zero-ing of shredded items.
    def set_zero(self, to_shred):
        self.zero = to_shred

    ## Translate to proper properties.
    def translate(self, item):
        if item[0] == "shr.iter":
            try:
                item[1] = int(item[1])
                self.iterations = item[1]
            except ValueError:
                return
        if item[0]=="shr.remove":
            self.remove_shredded = self.util.str2bool(item[1])
        if item[0]=="shr.zero":
            self.zero = self.util.str2bool(item[1])
        return

    def close_io():
        return self.props.close
        


