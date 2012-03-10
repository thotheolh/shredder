#!/usr/bin/env python
import sys, urllib, os, time
from gi.repository import Gtk, Gdk #gtk 3(!) library.

from shreddable import shreddable #shreddable class

license = """
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

version = "1.4 Pre-Alpha"

class UI(Gtk.Window):
	def __init__(self): #constructor
		super(Gtk.Window, self).__init__()
		
		#a few necessary variables
		self.filenames = []
		self.shred_list = []
		self.dialog_response = Gtk.ResponseType.CANCEL
		
		#preferences dialog stuff
		self.iterations = Gtk.SpinButton()
		self.iterations.set_adjustment(Gtk.Adjustment(0, 1, 20, 1, 10, 0))
		
		self.check_remove = Gtk.CheckButton(label="Remove files when shredded")
		
		self.check_zero = Gtk.CheckButton(label="Write files over with zeros")
		
		self.pref_close = Gtk.Button(stock=Gtk.STOCK_CLOSE)
		self.pref_close.connect("clicked", self.on_pref_quit)
		
		self.pref_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.pref_vbox.pack_start(self.check_remove, False, False, 0)
		self.pref_vbox.pack_start(self.check_zero, False, False, 0)
		self.pref_vbox.pack_start(self.iterations, False, False, 0)
		
		#setup the main window
		self.set_default_size(600, 400)
		self.set_title("shredder")
		self.connect("destroy", self.on_quit)
		
		#An action group for the menus
		self.actions = Gtk.ActionGroup("menu actions")
		
		
		#menu stuff
		self.menuxml = """
		<ui>
		<menubar name='MenuBar'>
			<menu action='File'>
				<menuitem action = 'FileQuit' />
				<menuitem action = 'FileFile' />
				<menuitem action = 'FileFolder' />
				<menuitem action = 'FileTrash' />
			</menu>
			<menu action='Edit'>
				<menuitem action = 'EditPref' />
			</menu>
			<menu action='Help'>
				<menuitem action ='HelpAbout' />
			</menu>
		</menubar>
		</ui>
		"""
		self.menumanager = Gtk.UIManager()
		self.menumanager.add_ui_from_string(self.menuxml)
		self.menumanager.insert_action_group(self.actions)
		
		self.action_file = Gtk.Action("File", "File", None, None)
		self.action_edit = Gtk.Action("Edit", "Edit", None, None)
		self.action_help = Gtk.Action("Help", "Help", None, None)
		self.action_file_quit = Gtk.Action("FileQuit", "Quit", None, None)
		self.action_file_file = Gtk.Action("FileFile", "Open a file", None, None)
		self.action_file_trash = Gtk.Action("FileTrash", "Open trash", None, None)
		self.action_file_folder = Gtk.Action("FileFolder", "Open a folder", None, None)
		self.action_edit_pref = Gtk.Action("EditPref", None, None, Gtk.STOCK_PREFERENCES)
		self.action_help_about = Gtk.Action("HelpAbout", None, None, Gtk.STOCK_ABOUT)
		
		self.action_file_quit.connect("activate", self.on_quit)
		self.action_file_file.connect("activate", self.on_open_file)
		self.action_file_folder.connect("activate", self.on_open_folder)
		self.action_file_trash.connect("activate", self.sidelist_add_trash)
		self.action_edit_pref.connect("activate", self.on_open_pref)
		self.action_help_about.connect("activate", self.on_help)
		
		self.actions.add_action(self.action_file)
		self.actions.add_action(self.action_help)
		self.actions.add_action(self.action_file_quit)
		self.actions.add_action(self.action_file_file)
		self.actions.add_action(self.action_file_folder)
		self.actions.add_action(self.action_file_trash)
		self.actions.add_action(self.action_edit)
		self.actions.add_action(self.action_edit_pref)
		self.actions.add_action(self.action_help_about)
		
		#The menu
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
		self.dnd_area.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
		self.dnd_area.connect("drag-data-received", self.on_drag_data)
		
		#A Button to shred everything
		self.shred = Gtk.Button("Shred files")
		self.shred.connect("clicked", self.shred_all)
	
		#A Button to add trash
		self.trash = Gtk.Button("Add Trash")
		self.trash.connect("clicked", self.sidelist_add_trash)
		
		#A Gtk.Button to hold necessary buttons
		self.controlpanel = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
		self.controlpanel.pack_end(self.shred, False, False, 0)
		self.controlpanel.pack_end(self.trash, False, False, 0)
		
		#A Gtk.Box to hold the controlpanel and dnd_area
		self.rightbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.rightbox.pack_start(self.dnd_area, True, True, 0)
		self.rightbox.pack_start(self.controlpanel, False, False, 0)
		
		#A Gtk.Box to hold the sidelist and any future widgets
		self.leftbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.leftbox.pack_start(self.sidelist, True, True, 0)
		
		
		#An About Dialog, where the developers get to show off.
		#If you're a contributor, please add yourself here.
		self.about_dialog = Gtk.AboutDialog()
		self.about_dialog.set_program_name("Shredder")
		self.about_dialog.set_website("http://code.google.com/p/shredder")
		self.about_dialog.set_license(license)
		self.about_dialog.set_authors([ "Tay Thotheolh <twzgerald@gmail.com>", "Michael Rawson <michaelrawson76@gmail.com>"])
		self.about_dialog.set_version(version)
		
		#A progress bar, for showing the shredded-ness.
		self.progress = Gtk.ProgressBar()
		self.progress.set_text("Idle")
		
		#A status bar for user information
		self.status = Gtk.Statusbar()
		self.status.push(0, "Idle")
		
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
		self.masterbox.pack_start(self.progress, False, False, 0)
		self.masterbox.pack_start(self.status, False, False, 0)
		
		self.add(self.masterbox)
		self.show_all()
		Gtk.main()
		
	#on quitting...
	def on_quit(self, padding):
		Gtk.main_quit()
		
	def on_pref_quit(self, padding):
		self.pref_window.destroy()
		
	#on opening file
	def on_open_file(self, padding):
		dialog = Gtk.FileChooserDialog("Open a file for shredding", self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		
		response = dialog.run()
        
		if response == Gtk.ResponseType.OK:
			self.sidelist_add_item(shreddable(dialog.get_filename(), self.iterations.get_value(), self.check_zero.get_active(), self.check_remove.get_active(), self))
			
		dialog.destroy()
		
	#on opening folder
	def on_open_folder(self, padding):
		
		dialog = Gtk.FileChooserDialog("Open a folder for shredding", self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		response = dialog.run()
        
		if response == Gtk.ResponseType.OK:
			self.sidelist_add_item(shreddable(dialog.get_filename(), self.iterations.get_value(), self.check_zero.get_active(), self.check_remove.get_active(), self))
			
		dialog.destroy()
		
	#on preferences
	def on_open_pref(self, padding):
		self.pref_window = Gtk.Window()
		self.pref_window.set_default_size(250, 300)
		self.pref_window.set_title("Preferences")
		self.pref_window.connect("destroy", self.on_pref_quit)
		self.pref_window.add(self.pref_vbox)
		self.pref_window.show_all()

	#on about
	def on_help(self, padding):
		self.about_dialog.run()
		self.about_dialog.hide()
	
	#add a generic item to the list
	def sidelist_add_item(self, shredinst):
		self.shred_list.append(shredinst)
		itemstring = shredinst.filename
		self.sidelist_model.append(row = [itemstring])
		self.filenames.append(itemstring)
			
	#add a trash entry to the list
	def sidelist_add_trash(self, button):
		if(self.trash.get_sensitive() != False):	
			home = os.getenv("HOME")
			trash = home + "/.local/share/Trash/files"
			trashshred = shreddable(trash, self.iterations.get_value(), False, False, self)
			trashshred.filename = trash
			self.sidelist_add_item(trashshred)
			self.trash.set_sensitive(False)
		
	#shred!
	def shred_all(self, button):
		self.progress.set_fraction(0)
		for items in self.shred_list:
			items.destroy()
			self.filenames.remove(items.filename)
			
		self.sidelist_model.clear()
		self.trash.set_sensitive(True)
		self.filenames = []
		self.shred_list = []
		self.progress.set_fraction(0)
		self.status.push(0, "Idle")
			
			
	def on_drag_data(self, widget, drag_context, x, y, data, info, time):
		print("Something dropped")
		
	
	#output text
	def insertText(self, output):
		self.progress.pulse()
		self.status.push(01, output)
		
		#nasty hack to give the thread control back to Gtk temporarily so the interface doesn't freeze while
		#processing the files. TODO: better threading control.
		while Gtk.events_pending():
			Gtk.main_iteration()
		
	

	
		
				
		

