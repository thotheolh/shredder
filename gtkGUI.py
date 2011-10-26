#!/usr/bin/python

import sys

importStatus = False

try:
	from gtk import *
	importStatus = True

except ImportError:
    print "PyGTK module does not exist. Can't launch GUI !"
    print "Please download and install GTK and PyGTK."
    importStatus = False

if importStatus:

    class gtkGUI():

        def __init__(self):
            print 'gtkGUI imported'

        def startGUI(self):
            print 'GUI Started'
            return None

        def checkGtkVersion(self):
            return gtk.gtk_version
        

        def checkPyGTKVersion(self):
            return gtk.pygtk_version


