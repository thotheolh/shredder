#!/usr/bin/env python
import sys, urllib, os
from gi.repository import Gtk #gtk 3(!) library.

from shreddable import shreddable #shreddable class

class UI(Gtk.Window):
	def __init__(self): #constructor
		super(Gtk.Window, self).__init__()
		
		#a few necessary variables
		self.filenames = []
		
		#setup the window
		self.set_default_size(600, 400)
		self.set_title("shredder")
		self.connect("destroy", self.on_quit)
		
		#An action group for the menus
		self.actions = Gtk.ActionGroup("menu actions")
		
		
		#menu stuff
		self.menuxml = """
		<ui>
		<menubar name='MenuBar'>
			<menu action='FileMenu'>
				<menuitem action='FileQuit' />
			</menu>
		</menubar>
		</ui>
		"""
		
		self.menumanager = Gtk.UIManager()
		self.menumanager.add_ui_from_string(self.menuxml)
		self.menumanager.insert_action_group(self.actions)
		self.action_file = Gtk.Action("FileMenu", "File", None, None)
		self.action_file_quit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
		self.action_file_quit.connect("activate", self.on_quit)
		self.actions.add_action(self.action_file)
		self.actions.add_action(self.action_file_quit)
		self.menu = self.menumanager.get_widget("/MenuBar")
		
		
		#a Gtk.TreeView showing the files, and associated objects
		self.sidelist = Gtk.TreeView()
		self.sidelist_model = Gtk.ListStore(str)
		self.sidelist_column = Gtk.CellRendererText()
		self.sidelist_title = Gtk.TreeViewColumn("Files")
		
		#setting up the TreeView
		self.sidelist.set_model(self.sidelist_model)
		self.sidelist_title.pack_start(self.sidelist_column, False)
		self.sidelist_title.add_attribute(self.sidelist_column, "text", 0)
		self.sidelist.append_column(self.sidelist_title)
			
		#A place for drag and drop, currently not functional (Tay fix!)
		self.dnd_area = Gtk.Label()
		self.dnd_area.set_label("Drag files here to add them")
		
		#a Gtk.SpinButton for the number of iterations
		self.iterations = Gtk.SpinButton()
		self.iterations.set_adjustment(Gtk.Adjustment(0, 1, 20, 1, 10, 0))
		self.iterations_label = Gtk.Label("Severity")
		
		#A Button to shred everything
		self.shred = Gtk.Button("Shred files")
		self.shred.connect("clicked", self.shred_all)
		
		#A Button to close
		self.close = Gtk.Button(stock=Gtk.STOCK_CLOSE)
		self.close.connect("clicked", Gtk.main_quit)
		
		#A Button to add trash
		self.trash = Gtk.Button("Add Trash")
		self.trash.connect("clicked", self.sidelist_add_trash)
		
		#A Gtk.Grid to hold three buttons and a spinnerbutton
		self.controlpanel = Gtk.Grid()
		self.controlpanel.attach(self.iterations, 0, 0, 1, 1)
		self.controlpanel.attach(self.shred, 1, 0, 1, 1)
		self.controlpanel.attach(self.trash, 0, 1, 1, 1)
		self.controlpanel.attach(self.close, 1, 1, 1, 1)
		
		#A Gtk.Box to hold the controlpanel and dnd_area
		self.rightbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.rightbox.pack_start(self.dnd_area, True, True, 0)
		self.rightbox.pack_start(self.controlpanel, False, False, 0)
		
		#A Gtk.Box to hold the sidelist and any future widgets
		self.leftbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.leftbox.pack_start(self.sidelist, True, True, 0)
		
		#the main box for the window
		self.mainbox = Gtk.Box()
		self.mainbox.set_orientation(Gtk.Orientation.HORIZONTAL)
		self.mainbox.pack_start(self.leftbox, True, True, 0)
		self.mainbox.pack_start(self.rightbox, True, True, 0)
		
		
		
		#include mainbox and menu
		self.masterbox = Gtk.Box()
		self.masterbox.set_orientation(Gtk.Orientation.VERTICAL)
		self.masterbox.pack_start(self.menu, False, False, 0)
		self.masterbox.pack_start(self.mainbox, True, True, 0)
		
		self.add(self.masterbox)
		self.show_all()
		Gtk.main()
		
	#on quitting...
	def on_quit(self, padding):
		Gtk.main_quit()
	
	#add a generic item to the list
	def sidelist_add_item(self, shredinst):
		itemstring = shredinst.filename
		self.sidelist_model.append(row = [itemstring])
		self.filenames += itemstring
			
	#add a trash entry to the list
	def sidelist_add_trash(self, button):
		home = os.getenv("HOME")
		trash = home + ".local/share/Trash/files"
		trashshred = shreddable()
		trashshred.filename = trash
		self.sidelist_add_item(trashshred)
		self.trash.set_sensitive(False)
		
	#shred!
	def shred_all(self, button):
		print(self.filenames)


	
		
				
		

