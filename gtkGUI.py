#!/usr/bin/python

import sys

importStatus = False

try:
	import pygtk
	pygtk.require('2.0')
	import gtk
	importStatus = True

except ImportError:
    print "PyGTK module does not exist. Can't launch GUI !"
    print "Please download and install GTK and PyGTK."
    importStatus = False

<<<<<<< HEAD
if importStatus:

    class gtkGUI():

        def __init__(self):
            print "gtkGUI imported"

        def startGUI(self):
            print "GUI Started"
            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.window.set_border_width(10)
            self.window.connect("destroy", self.destroy)

			## Labels
            self.filelbl = gtk.Label("File / Folder: ")
            self.iterationlbl = gtk.Label("Shred Iterations: ")
            self.zerolbl = gtk.Label("Zero-ing")

			## Buttons
            self.shredbtn = gtk.Button("Shred !")
            self.filechoosebtn = gtk.Button("...")
            self.trashbtn = gtk.Button("Trash")

			## Check Boxes
            self.zero = gtk.CheckButton(label=None)

			## Text Fields
            self.filenametf = gtk.Entry(max=0)
            self.filenametf.set_max_length(20)
            self.itertf = gtk.Entry(max=0)
            self.itertf.set_max_length(8)

            ## Text Area
            ## self.status = gtk.

			## Packing widgets into window
            self.window.add(self.shredbtn)

			## Presenting window
            self.window.show_all()
            gtk.main()
            return None

        def checkGtkVersion(self):
            return gtk.gtk_version
        

        def checkPyGTKVersion(self):
            return gtk.pygtk_version

        def destroy(self, widget, data=None):
            return gtk.main_quit()
=======
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
>>>>>>> 68fd6227b7f485b6e5e8816ef64f22b968ccf8c3
