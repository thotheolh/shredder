#!/usr/bin/env python

## This class does NOT handle the File I/O of the actual settings. They are to simply handle, hold and translate settings.
class settings():

    version = "2.0 (Pre-Alpha)" #Hard code version.
    iterations = "5"            #Default.
    remove_shredded = False  #Default.
    zero = True              #Default.

    ## Gets settings. Calls I/O to read files settings and load in.
    def get():

    ## Save existing settings. Calls up I/O methods in another class to do the physical saving of settings.
    def commit():

    ## Get shredding iterations.
    def get_shred_iterations():
        return self.iterations

    ## Set shredding iterations.
    def set_shred_iterations(iters):
        self.iterations = iters

    ## Check if shredded items are removed.
    def is_remove_shredded():
        return self.remove_shredded

    ## Set removal of shredded items.
    def set_remove_shredded(to_remove):
        self.remove_shredded = to_remove

    ## Check if shredded items are zeroed.
    def is_zero():
        return self.zero

    ## Set zero-ing of shredded items.
    def set_zero(to_shred):
        self.zero = to_shred
