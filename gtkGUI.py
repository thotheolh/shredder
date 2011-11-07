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

def gtkGUI():
	try:
		import gtk
		importStatus = True

	except ImportError:
		print "PyGTK module does not exist. Can't launch GUI !"
		print "Please download and install GTK and PyGTK."
		importStatus = False
	import gtk
	window=gtk.Window()
	window.connect('destroy', lambda w: gtk.main_quit())
	window.set_size_request(400, 600)
	window.show_all()
	gtk.main()
