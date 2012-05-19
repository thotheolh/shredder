#!/usr/bin/env python
import sys, urllib, os, time, gettext
from gi.repository import Gtk, Gdk #gtk 3(!) library.
from shreddable import shreddable #shreddable class
from settings import settings
from util import util

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

class gtk3(Gtk.Window):

	def __init__(self): # Constructor
		super(Gtk.Window, self).__init__()
		print "Starting Gnome 3 Interface"
		
		self.filenames = []
		self.shred_list = []
		self.settings = settings()
		self.dialog_response = Gtk.ResponseType.CANCEL

		self.TARGETS = [('MY_TREE_MODEL_ROW',Gtk.TargetFlags.SAME_WIDGET,0),
			   ('text/plain', 0, 1),
			   ('TEXT', 0, 2),
			   ('STRING',0, 3)
			   ]
		
		## Main window
		self.set_default_size(650, 400)
		self.set_border_width(10)
		self.set_title(_("Shredder " + version))
		self.connect("destroy", self.on_quit)	
		self.set_icon_from_file(util().get_resource("img/shredder256.png"))

		#An action group for the menus
                self.actions = Gtk.ActionGroup("menu actions") 

		# menu and toolbar stuff
                self.menuxml = """
                <ui>
                <menubar name='MenuBar'>
                        <menu action='File'>
                                <menuitem action = 'FileFile' />
                                <menuitem action = 'FileFolder' />
                                <menuitem action = 'FileQuit' />
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
                
                self.action_file = Gtk.Action("File", _("File"), None, None)
                self.action_edit = Gtk.Action("Edit", _("Edit"), None, None)
                self.action_help = Gtk.Action("Help", _("Help"), None, None)
                self.action_file_file = Gtk.Action("FileFile", _("Open a file"), None, None)
                self.action_file_folder = Gtk.Action("FileFolder", _("Open a folder"), None, None)
                self.action_file_quit = Gtk.Action("FileQuit", _("Quit"), None, None)
                self.action_edit_pref = Gtk.Action("EditPref", None, None, Gtk.STOCK_PREFERENCES)
                self.action_help_about = Gtk.Action("HelpAbout", None, None, Gtk.STOCK_ABOUT)
                
                self.action_file_file.connect("activate", self.on_open_file)
                self.action_file_folder.connect("activate", self.on_open_folder)
                self.action_file_quit.connect("activate", self.on_quit)
                self.action_edit_pref.connect("activate", self.on_open_pref)
                self.action_help_about.connect("activate", self.on_help)
                
                self.actions.add_action(self.action_file)
                self.actions.add_action(self.action_help)
                self.actions.add_action(self.action_file_file)
                self.actions.add_action(self.action_file_folder)
                self.actions.add_action(self.action_file_quit)
                self.actions.add_action(self.action_edit)
                self.actions.add_action(self.action_edit_pref)
                self.actions.add_action(self.action_help_about)
                
                #The menu
                self.menu = self.menumanager.get_widget("/MenuBar")
        
        	#toolbar        
		self.toolbar = Gtk.Toolbar()
		self.toolbar.set_style(Gtk.ToolbarStyle.TEXT)
		
		#toolbuttons
		
		self.addfile = Gtk.ToolButton()
		self.addfile.set_label("Add File")
		'''self.addfileimg = Gtk.Image() #Failed attempt to add icon for ToolButton
            	self.addfileimg.set_from_file(self.get_resource("img/file.png"))
		self.addfile.set_icon_widget(self.addfileimg)'''
		self.addfile.connect("clicked", self.on_open_file)

		self.addfolder = Gtk.ToolButton()
		self.addfolder.set_label("Add Folder")
		self.addfolder.connect("clicked", self.on_open_folder)
		
		self.trash = Gtk.ToolButton()
		self.trash.set_label("Shred Trash")
		self.trash.connect("clicked", self.sidelist_add_trash)

		self.remove = Gtk.ToolButton()
		self.remove.set_label("Remove File/Folder")
		self.remove.connect("clicked", self.clear_selected)
		
		self.removeall = Gtk.ToolButton()
		self.removeall.set_label("Clear List")
		self.removeall.connect("clicked", self.clear_treeview)

		self.prefbtn = Gtk.ToolButton()
		self.prefbtn.set_label("Preferences")
		self.prefbtn.connect("clicked", self.on_open_pref)
		
		
		self.toolbar.insert(self.prefbtn, 0)
		self.toolbar.insert(self.removeall, 0)
		self.toolbar.insert(self.remove, 0)
		self.toolbar.insert(self.trash, 0)
		self.toolbar.insert(self.addfolder, 0)
		self.toolbar.insert(self.addfile, 0)

		# Tree showing the files, and associated objects
		self.sidelist = Gtk.TreeView()
		self.sidelist_model = Gtk.ListStore(str)
		self.sidelist_column = Gtk.CellRendererText()
		self.sidelist_title = Gtk.TreeViewColumn(_("Files and folders for shredding... (You can drag and drop files and folders below)"))
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
		
		#An About Dialog, where the developers get to show off.
		#If you're a contributor, please add yourself here.
		self.about_dialog = Gtk.AboutDialog()
		self.about_dialog.set_program_name(_("Shredder"))
		self.about_dialog.set_website("http://code.google.com/p/shredder")
		self.about_dialog.set_license(license)
		self.about_dialog.set_authors([ "Tay Thotheolh <twzgerald@gmail.com>", "Michael Rawson <michaelrawson76@gmail.com>"])
		self.about_dialog.set_version(version)

		# Shred button and box
		self.shredbtn = Gtk.Button()
		self.shredbtn.connect("clicked", self.shred_all, None)
		self.shredimg = Gtk.Image()
		self.shredimg.set_from_file(util().get_resource("img/shred.png"))
		self.shredbtn.add(self.shredimg)
		self.shredbox = Gtk.HBox()		
		self.shredbox.set_orientation(Gtk.Orientation.HORIZONTAL)
		self.shredbox.pack_end(self.shredbtn, False, False, 0)
		
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
		self.mainbox.pack_start(self.sidelist, True, True, 5)
		
		#include mainbox and menu
		self.masterbox = Gtk.VBox()
		self.masterbox.set_orientation(Gtk.Orientation.VERTICAL)
		self.masterbox.pack_start(self.menu, False, False, 0)
		self.masterbox.pack_start(self.toolbar, False, False, 0)
		self.masterbox.pack_start(self.mainbox, True, True, 0)		
		self.masterbox.pack_start(self.shredbox, False, False, 5)
		self.separator = Gtk.HSeparator()
		self.masterbox.pack_start(self.separator, False, False, 0)
		self.masterbox.pack_start(self.progress, False, False, 5)
		self.masterbox.pack_start(self.status, False, False, 0)
		
		self.add(self.masterbox)
		self.show_all()
		Gtk.main()
		
	#on quitting...
	def on_quit(self, padding):
		Gtk.main_quit()
		
	def on_pref_quit(self, padding):
		self.settings.set_shred_iterations(self.check_iterations.get_value())
		self.settings.set_remove_shredded(self.check_remove.get_active())
		self.settings.set_zero(self.check_zero.get_active())
		self.settings.commit()
		self.pref_window.destroy()
		
	#on opening file
	def on_open_file(self, padding):
		dialog = Gtk.FileChooserDialog(_("Open a file for shredding"), self, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		
		response = dialog.run()
        
		if response == Gtk.ResponseType.OK:
			self.sidelist_add_item(shreddable(dialog.get_filename(), self.settings.get_shred_iterations(), self.settings.is_zero(), self.settings.is_remove_shredded(), self))
			
		dialog.destroy()
		
	#on opening folder
	def on_open_folder(self, padding):
		
		dialog = Gtk.FileChooserDialog(_("Open a folder for shredding"), self, Gtk.FileChooserAction.SELECT_FOLDER, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		response = dialog.run()
        
		if response == Gtk.ResponseType.OK:
			self.sidelist_add_item(shreddable(dialog.get_filename(), self.settings.get_shred_iterations(), self.settings.is_zero(), self.settings.is_remove_shredded(),self))
			
		dialog.destroy()
		
	#on preferences
	def on_open_pref(self, padding):
		self.check_iterations = Gtk.SpinButton()
		self.check_iterations.set_adjustment(Gtk.Adjustment(int(self.settings.get_shred_iterations()), 1, sys.float_info.max, 1, 10, 0))
		
		self.check_remove = Gtk.CheckButton(label=_("Remove files when shredded"))
		self.check_remove.set_active(self.settings.is_remove_shredded())
		
		self.check_zero = Gtk.CheckButton(label=_("Write files over with zeros"))
		self.check_zero.set_active(self.settings.is_zero())
		
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
		trashshred = shreddable(trash, self.settings.get_shred_iterations(), self.settings.is_zero(), self.settings.is_remove_shredded(), self)
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
	
	#Set general status message.
	def set_general_status(self, output):
		self.progress.pulse()
		self.status.push(01, output)
	
	# Set shredding related status message.
	def set_shred_status(self, output):
		self.progress.pulse()
		if self.settings.is_remove_shredded():
		output = output + "/" + len(self.sidelist_model) + " Done."
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

		
	

	
		
				
		
