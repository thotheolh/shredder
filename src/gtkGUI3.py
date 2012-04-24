#!/usr/bin/env python
import sys, urllib, os, time, gettext
from gi.repository import Gtk, Gdk #gtk 3(!) library.

from shreddable import shreddable #shreddable class

t = gettext.translation('shredder', 'locale', fallback=True)
_ = t.ugettext

license = _("This program is free software; you can redistribute it and/or\n\
modify it under the terms of the GNU General Public License\n\
as published by the Free Software Foundation; either version 2\n\
of the License, or (at your option) any later version.\n\
This program is distributed in the hope that it will be useful,\n\
but WITHOUT ANY WARRANTY; without even the implied warranty of\n\
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n\
GNU General Public License for more details.\n\
You should have received a copy of the GNU General Public License\n\
along with this program; if not, write to the Free Software\n\
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.\n\
")

version = "2.0 (Pre-Alpha)"

class UI(Gtk.Window):
	def __init__(self): # Constructor
		super(Gtk.Window, self).__init__()
		print "Starting Gnome 3 Interface"
		
		self.filenames = []
		self.shred_list = []
		self.iterations = 1
		self.remove = False
		self.zero = False
		self.dialog_response = Gtk.ResponseType.CANCEL

		self.TARGETS = [('MY_TREE_MODEL_ROW',Gtk.TargetFlags.SAME_WIDGET,0),
			   ('text/plain', 0, 1),
			   ('TEXT', 0, 2),
			   ('STRING',0, 3)
			   ]
		
		# Main window
		self.set_default_size(650, 400)
        self.set_border_width(10)
		self.set_title(_("Shredder " + version))
		self.connect("destroy", self.on_quit)
		
		# Tree showing the files, and associated objects
		self.sidelist = Gtk.TreeView()
		self.sidelist_model = Gtk.ListStore(str)
		self.sidelist_column = Gtk.CellRendererText()
		self.sidelist_title = Gtk.TreeViewColumn(_("Files and folders for shredding..."))
		self.sidelist.set_model(self.sidelist_model)
		self.sidelist_title.pack_start(self.sidelist_column, False)
		self.sidelist_title.add_attribute(self.sidelist_column, "text", 0)
		self.sidelist.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,self.TARGETS,Gdk.DragAction.DEFAULT|Gdk.DragAction.MOVE)
		self.sidelist.enable_model_drag_dest(self.TARGETS, Gdk.DragAction.DEFAULT)
		self.sidelist.drag_dest_add_text_targets()
		self.sidelist.drag_source_add_text_targets()
		self.sidelist.connect("drag_data_get", self.drag_data_get_data)
		self.sidelist.connect("drag_data_received", self.drag_data_received_data)
		self.sidelist.append_column(self.sidelist_title)
			
		#A place for drag and drop, currently not functional (Tay fix!)
		#self.dnd_area = Gtk.Label()
		#self.dnd_area.set_label(_("Drag files here to add them"))
		#self.dnd_area.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
		#self.dnd_area.connect("drag-data-received", self.on_drag_data)
		
		# Button to shred everything
		self.shred = Gtk.Button(_("Shred Files"))
		self.shred.connect("clicked", self.shred_all)
	
		# Button to add trash
		self.trash = Gtk.Button(_("Shred Trash"))
		self.trash.connect("clicked", self.sidelist_add_trash)

		# Button to add files for shredding
		self.addfile = Gtk.Button(_("Add File"))
		self.addfile.connect("clicked", self.on_open_file)

		# Button to add folder for shredding
		self.addfolder = Gtk.Button(_("Add Folder"))
		self.addfolder.connect("clicked", self.on_open_folder)

		# Button to remove selected item
		self.remove = Gtk.Button(_("Remove Item"))
		self.remove.connect("clicked", self.clear_selected)

		# Button to remove all items in tree
		self.removeall = Gtk.Button(_("Clear All Items"))
		self.removeall.connect("clicked", self.clear_treeview)
		
		#A Gtk.Button to hold necessary buttons
		self.controlpanel = Gtk.HBox(orientation = Gtk.Orientation.HORIZONTAL)
		self.controlpanel.pack_end(self.shred, False, False, 0)
		self.controlpanel.pack_end(self.addfolder, False, False, 0)
		self.controlpanel.pack_end(self.addfile, False, False, 0)
		self.controlpanel.pack_end(self.remove, False, False, 0)
		self.controlpanel.pack_end(self.removeall, False, False, 0)
		self.controlpanel.pack_end(self.trash, False, False, 0)
		
		#A Gtk.Box to hold the controlpanel and dnd_area
		#self.rightbox = Gtk.VBox(orientation = Gtk.Orientation.VERTICAL)
		#self.rightbox.pack_start(self.dnd_area, True, True, 0)
		#self.rightbox.pack_start(self.controlpanel, False, False, 0)
		
		#A Gtk.Box to hold the sidelist and any future widgets
		self.box = Gtk.VBox(orientation = Gtk.Orientation.VERTICAL)
		self.box.pack_start(self.sidelist, True, True, 0)		
		self.box.pack_start(self.controlpanel, False, False, 10)
		
		#An About Dialog, where the developers get to show off.
		#If you're a contributor, please add yourself here.
		self.about_dialog = Gtk.AboutDialog()
		self.about_dialog.set_program_name(_("Shredder"))
		self.about_dialog.set_website("http://code.google.com/p/shredder")
		self.about_dialog.set_license(license)
		self.about_dialog.set_authors([ "Tay Thotheolh <twzgerald@gmail.com>", "Michael Rawson <michaelrawson76@gmail.com>"])
		self.about_dialog.set_version(version)
		
		#A progress bar, for showing the shredded-ness.
		self.progress = Gtk.ProgressBar()
		self.progress.set_text(_("Idle"))
		
		#A status bar for user information
		self.status = Gtk.Statusbar()
		self.status.push(0, _("Idle"))
		
		#A separator to define left and right
		self.main_sep = Gtk.Separator()
		self.main_sep.set_orientation(Gtk.Orientation.VERTICAL)
		
		#the main box for the window
		self.mainbox = Gtk.HBox()
		self.mainbox.set_orientation(Gtk.Orientation.HORIZONTAL)
		#self.mainbox.pack_start(self.leftbox, True, True, 5)
		#self.mainbox.pack_start(self.main_sep, False, True, 5)
		#self.mainbox.pack_start(self.rightbox, True, True, 5)
		self.mainbox.pack_start(self.box, True, True, 5)
		
		#include mainbox and menu
		self.masterbox = Gtk.VBox()
		self.masterbox.set_orientation(Gtk.Orientation.VERTICAL)
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
		self.iterations = self.check_iterations.get_value()
		self.remove = self.check_remove.get_active()
		self.zero = self.check_zero.get_active()
		self.pref_window.destroy()
		
	#on opening file
	def on_open_file(self, padding):
		dialog = Gtk.FileChooserDialog(_("Open a file for shredding"), self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		
		response = dialog.run()
        
		if response == Gtk.ResponseType.OK:
			self.sidelist_add_item(shreddable(dialog.get_filename(), self.iterations, self.zero, self.remove, self))
			
		dialog.destroy()
		
	#on opening folder
	def on_open_folder(self, padding):
		
		dialog = Gtk.FileChooserDialog(_("Open a folder for shredding"), self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		response = dialog.run()
        
		if response == Gtk.ResponseType.OK:
			self.sidelist_add_item(shreddable(dialog.get_filename(), self.iterations, self.zero, self.remove, self))
			
		dialog.destroy()
		
	#on preferences
	def on_open_pref(self, padding):
		self.check_iterations = Gtk.SpinButton()
		self.check_iterations.set_adjustment(Gtk.Adjustment(self.iterations, 1, 20, 1, 10, 0))
		
		self.check_remove = Gtk.CheckButton(label=_("Remove files when shredded"))
		self.check_remove.set_active(self.remove)
		
		self.check_zero = Gtk.CheckButton(label=_("Write files over with zeros"))
		self.check_zero.set_active(self.zero)
		
		self.pref_close = Gtk.Button(stock=Gtk.STOCK_CLOSE)
		self.pref_close.connect("clicked", self.on_pref_quit)
		
		self.pref_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.pref_vbox.pack_start(self.check_remove, False, False, 0)
		self.pref_vbox.pack_start(self.check_zero, False, False, 0)
		self.pref_vbox.pack_start(self.check_iterations, False, False, 0)
		self.pref_window = Gtk.Window()
		self.pref_window.set_default_size(250, 300)
		self.pref_window.set_title(_("Preferences"))
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
		home = os.getenv("HOME")
		trash = home + "/.local/share/Trash/files"
		trashshred = shreddable(trash, self.iterations, self.zero, self.remove, self)
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
		self.status.push(0, _("Idle"))
	
	#output text
	def insertText(self, output):
		self.progress.pulse()
		self.status.push(01, output)
		
		#nasty hack to give the thread control back to Gtk temporarily so the interface doesn't freeze while
		#processing the files. TODO: better threading control.
		while Gtk.events_pending():
			Gtk.main_iteration()

	def drag_data_get_data(self, treeview, context, selection, target_id, etime):
        	treeselection = treeview.get_selection()
        	model, iter = treeselection.get_selected()
        	data = bytes(model.get_value(iter, 0), "utf-8")
        	selection.set(selection.get_target(), 8, data)

    	def drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
        	model = treeview.get_model()
        	data = selection.get_data().decode("utf-8")
		data = self.cleanse_drag_input(data)
        	model.append([data])
        	if context.get_actions() == Gdk.DragAction.MOVE:
        	    context.finish(True, True, etime)
		self.test()
        	return

	def cleanse_drag_input(self, uri):
		print "cleanse_drag_input() - uri - "+uri
		path = ""
        	if uri.startswith("file:\\\\\\"): # windows
        	    # print "windows"
        	    path = uri[8:] # 8 is len('file:///')
        	elif uri.startswith("file://"): # nautilus, rox
        	    # print "nautilus"
        	    path = uri[7:] # 7 is len('file://')
        	elif uri.startswith("file:"): # xffm
        	    # print "xffm"
        	    path = uri[5:] # 5 is len('file:')
        	path = urllib.url2pathname(path) # escape special chars
        	path = path.strip('\r\n\x00') # remove \r\n and NULL
        	return path

	def clear_selected(self, button):
		selection = self.sidelist.get_selection()
		model, iter = selection.get_selected()
		if iter:
			model.remove(iter)
		return

	def clear_treeview(self, button):
		self.sidelist_model = Gtk.ListStore(str)
		self.sidelist.set_model(self.sidelist_model)
		return

		
	

	
		
				
		

