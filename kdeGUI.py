#!/usr/bin/python

class kdeGUI:

    def __init__(self):
        print 'kdeGUI imported'

    def startGUI(self):
	print 'GUI Started'
        return None

    def checkGtkVersion(self):
        print gtk.gtk_version

    def checkPyGTKVersion(self):
        print gtk.pygtk_version
