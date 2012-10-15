#!/usr/bin/python

import sys
import os
import urllib
from shreddable import shreddable
from settings import settings
from util import util

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
    
if importStatus:

    class gtkGUI2():

        count = 0
        ttlcount = 0
        output = None
        filenametf = None
        chooser = None
        dnd_list = [ ( 'text/uri-list', 0, 80 ) ]
        cwd = os.getcwd()
        TARGETS = [
            ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
            ('text/plain', 0, 1),
            ('TEXT', 0, 2),
            ('STRING', 0, 3)]
        settings = settings()

        license = "This program is free software; you can redistribute it and/or\n\
        modify it under the terms of the GNU General Public License\n\
        as published by the Free Software Foundation; either version 2\n\
        of the License, or (at your option) any later version.\n\
        This program is distributed in the hope that it will be useful,\n\
        but WITHOUT ANY WARRANTY; without even the implied warranty of\n\
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n\
        GNU General Public License for more details.\n\
        You should have received a copy of the GNU General Public License\n\
        along with this program; if not, write to the Free Software\n\
        Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA."

        def __init__(self):
            print "Starting Gnome 2 Interface"
            self.startGUI()

        def startGUI(self):
            print "GUI Started"

            ## Main Window
            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.window.set_border_width(10)
            self.version = self.settings.get_version()
            self.window.set_title("Shredder " + self.version)
            self.window.set_default_size(650, 400)
            self.window.connect("destroy", self.destroy)
            self.window.set_icon_from_file(util().get_resource("img/shredder256.png"))
            
            ## Toolbar
            self.toolbar = gtk.Toolbar()
            self.toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
            self.toolbar.set_style(gtk.TOOLBAR_BOTH)
            self.toolbar.set_border_width(5)
            
            ## Labels
            self.statuslbl = gtk.Label("Idle")
            self.statuslbl.set_line_wrap(True)
            self.iterationlbl = gtk.Label("Shred Iterations: ")
            self.zerolbl = gtk.Label("Zero-ing: ")
            self.removelbl = gtk.Label("Remove: ")

            ## Spin Buttons
            self.adjustments = gtk.Adjustment(int(self.settings.get_shred_iterations()),1,sys.float_info.max, 1, 10, 0)
            self.check_iterations = gtk.SpinButton()
            self.check_iterations.set_adjustment(self.adjustments)

            ## Image Icons

            # Shred image
            self.shredimg = gtk.Image()
            self.shredimg.set_from_file(util().get_resource("img/shredder24.png"))
            # Filechooser image
            self.fileimg = gtk.Image()
            self.fileimg.set_from_file(util().get_resource("img/file.png"))

            # Folderchooser image
            self.folderimg = gtk.Image()
            self.folderimg.set_from_file(util().get_resource("img/folder.png"))

            # Trash image
            self.trashimg = gtk.Image()
            self.trashimg.set_from_file(util().get_resource("img/trash.png"))

            # Remove image
            self.rmimg = gtk.Image()
            self.rmimg.set_from_file(util().get_resource("img/remove.png"))

            # Clear image
            self.clrimg = gtk.Image()
            self.clrimg.set_from_file(util().get_resource("img/clear.png"))

            # Preferences image
            self.prefimg = gtk.Image()
            self.prefimg.set_from_file(util().get_resource("img/preferences.png"))

            # About image
            self.abtimg = gtk.Image()
            self.abtimg.set_from_file(util().get_resource("img/about.png"))
            

            ## Check Boxes
            self.zero = gtk.CheckButton(label=None)
            self.zero.set_active(self.settings.is_zero())
            self.remove = gtk.CheckButton(label=None)
            self.remove.set_active(self.settings.is_remove_shredded())
            
            ## Tree with scrolling
            self.scrolltree = gtk.ScrolledWindow()
            self.liststore = gtk.ListStore(str)
            self.tree = gtk.TreeView(self.liststore)
            self.cell = gtk.CellRendererText()
            self.tvcolumn = gtk.TreeViewColumn("Files and folders for shredding... (You can drag and drop files and folders below)", self.cell, text=0)
            self.tree.append_column(self.tvcolumn)
            self.tree.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT|gtk.gdk.ACTION_MOVE)
            self.tree.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT)
            self.tree.connect("drag_data_get", self.drag_data_get_data)
            self.tree.connect("drag_data_received", self.drag_data_received_data)
            self.scrolltree.add(self.tree)

            ## Adding items to toolbar
            self.toolbar.append_item("Shred", "Begin shredding files", "Private", self.shredimg, self.do_shred)
            self.toolbar.append_item("Add File", "Choose a file", "Private", self.fileimg, self.get_filechooser_callback)
            self.toolbar.append_item("Add Folder", "Choose a folder", "Private", self.folderimg, self.get_folderchooser_callback)
            self.toolbar.append_item("Add Trash", "Shred Trash bin", "Private", self.trashimg, self.shred_trash)
            self.toolbar.append_item("Remove Item", "Remove file/folder from shredding list", "Private", self.rmimg, self.clear_selected)
            self.toolbar.append_item("Clear List", "Clear shredding list", "Private", self.clrimg, self.clear_treeview)
            self.toolbar.append_item("Preferences","Shredder settings and preferences", "Private", self.prefimg, self.on_open_pref)
            self.toolbar.append_item("About", "About Shredder", "Private", self.abtimg, self.about)

            ## An About Dialog, where the developers get to show off.
		    #  If you're a contributor, please add yourself here.
            self.about_dialog = gtk.AboutDialog()
            self.about_dialog.set_program_name("Shredder")
            self.about_dialog.set_website("http://code.google.com/p/shredder")
            self.about_dialog.set_license(self.license)
            self.about_dialog.set_authors([ "Tay Thotheolh <twzgerald@gmail.com>", "Michael Rawson <michaelrawson76@gmail.com>"])
            self.about_dialog.set_version(self.version)

            ## Progress bar
            self.progress = gtk.ProgressBar()

            ## Packing widgets into window

            # Vertical box to contain all boxes
            self.vbox = gtk.VBox(homogeneous=False, spacing=0)  

            # toolbox to contain toolbar
            self.toolbox = gtk.HBox(homogeneous=False, spacing=0)
            self.vbox.pack_start(self.toolbar, expand=False, fill=False, padding=0)

            # treebox to contain treeview
            self.treebox = gtk.HBox(homogeneous=False, spacing=0)
            self.vbox.pack_start(self.scrolltree, expand=True, fill=True, padding=0)
            
            # Overall VBox
            self.mainbox = gtk.VBox(homogeneous=False, spacing=0)
            self.mainbox.pack_start(self.vbox, expand=True, fill=True, padding=0)
            self.statusbox = gtk.HBox(homogeneous=False, spacing=0)
            self.statusbox.pack_start(self.statuslbl, expand=False, fill=False, padding=0)
            self.separator = gtk.HSeparator()
            self.mainbox.pack_start(self.separator, expand=False, fill=False, padding=0)
            self.mainbox.pack_start(self.progress, expand=False, fill=False, padding=5)
            self.mainbox.pack_end(self.statusbox, expand=False, fill=False, padding=0)

            ## Presenting window    
            self.progress.show()
            self.toolbar.show()
            self.window.add(self.mainbox)
            self.window.show_all()
            gtk.main()
            return None

        ## Check GTK version
        def checkGtkVersion(self):
            return gtk.gtk_version
        
        ## Check PyGTK version
        def checkPyGTKVersion(self):
            return gtk.pygtk_version

        ## Closes main window
        def destroy(self, widget, data=None):
            self.settings.close_io
            return gtk.main_quit()

        ## Calls up about window
        def about(self, padding):
            self.about_dialog.run()
            self.about_dialog.hide()

	    ## Increment count counter
        def inc_count(self):
            self.count = self.count + 1

        ## Output status
        ## Need to upgrade for status label use
        def set_general_status(self, text):
            self.statuslbl.set_text(text)

        def set_shred_status(self, text):
            self.progress.set_fraction(float(self.count)/self.ttlcount)
            text = text + "   | " + str(self.count) + " / " + str(self.ttlcount) + " Done."
            self.statuslbl.set_text(text)
            while(gtk.events_pending()):
		        gtk.main_iteration()

        ## Trash bin selected for secure wiping
        def shred_trash(self, widget, data=None):
            loc = os.getenv("HOME")
            self.tree_add_item(loc + "/.local/share/Trash")

        ## Filechooser
        def get_filechooser_callback(self, widget, data=None):
            self.chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            self.chooser.set_default_response(gtk.RESPONSE_OK)
            self.chooser.set_current_folder(os.getenv("HOME"))
            response = self.chooser.run()
            if response == gtk.RESPONSE_OK:
                self.tree_add_item(self.chooser.get_filename())
            elif response == gtk.RESPONSE_CANCEL:
                self.chooser.destroy()
            self.chooser.destroy()

        ## Folderchooser
        def get_folderchooser_callback(self, widget, data=None):
            self.chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            self.chooser.set_default_response(gtk.RESPONSE_OK)
            self.chooser.set_current_folder(os.getenv("HOME"))
            response = self.chooser.run()
            if response == gtk.RESPONSE_OK:
                self.tree_add_item(self.chooser.get_filename())
            elif response == gtk.RESPONSE_CANCEL:
                self.chooser.destroy()
            self.chooser.destroy()

        def get_settings_box(self):
            self.settingsbox = gtk.VBox(homogeneous=False, spacing=0)
            self.iterbox = gtk.HBox(homogeneous=False, spacing=0)
            self.zerobox = gtk.HBox(homogeneous=False, spacing=0)
            self.rmbox = gtk.HBox(homogeneous=False, spacing=0)
            self.savesettingsbox = gtk.HBox(homogeneous=False, spacing=0)
            self.settingsbtn = gtk.Button("Save Preferences")
            self.settingsbtn.connect("clicked", self.do_save_prefs, None)
            
            self.iterbox.pack_start(self.iterationlbl, expand=False, fill=False, padding=5)
            self.iterbox.pack_start(self.check_iterations, expand=False, fill=True, padding=0)
            self.zerobox.pack_start(self.zerolbl, expand=False, fill=False, padding=5)
            self.zerobox.pack_start(self.zero, expand=False, fill=False, padding=0)
            self.rmbox.pack_start(self.removelbl, expand=False, fill=False, padding=5)
            self.rmbox.pack_start(self.remove, expand=False, fill=False, padding=0)
            self.savesettingsbox.pack_end(self.settingsbtn, expand=False, fill=False, padding=5)

            self.settingsbox.pack_start(self.iterbox, expand=False, fill=False, padding=5)
            self.settingsbox.pack_start(self.zerobox, expand=False, fill=False, padding=5)
            self.settingsbox.pack_start(self.rmbox, expand=False, fill=False, padding=5)
            self.settingsbox.pack_end(self.savesettingsbox, expand=False, fill=True, padding=5)
            return self.settingsbox

        def on_open_pref(self, widget, data=None):
            self.pref_window = gtk.Window()
            self.pref_window.set_default_size(250, 300)
            self.pref_window.set_title("Preferences")
            self.pref_window.connect("destroy", self.on_pref_quit)
            self.pref_window.add(self.get_settings_box())
            self.pref_window.show_all()

        def on_pref_quit(self, padding):
            self.iterations = self.check_iterations.get_value()
            self.is_remove = self.remove.get_active()
            self.is_zero = self.zero.get_active()
            self.pref_window.destroy()

        ## Disables widget
        def disable_widgets(self):
            self.toolbar.set_sensitive(False)
            self.tree.unset_rows_drag_source()
            self.tree.unset_rows_drag_dest()

        ## Enables widgets
        def enable_widgets(self):
            self.toolbar.set_sensitive(True)
            self.tree.enable_model_drag_source( gtk.gdk.BUTTON1_MASK, self.TARGETS, gtk.gdk.ACTION_DEFAULT|gtk.gdk.ACTION_MOVE)
            self.tree.enable_model_drag_dest(self.TARGETS, gtk.gdk.ACTION_DEFAULT)

        ## Get data when drag occurs inside the tree
        def drag_data_get_data(self, treeview, context, selection, target_id, etime):
            treeselection = treeview.get_selection()
            model, iter = treeselection.get_selected()
            data = model.get_value(iter, 0)
            selection.set(selection.target, 8, data)

        ## Receives the data that is dropped into the tree after the drag
        def drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
            data = selection.data
            lst = data.split('\r\n')
            if isinstance(lst, list):
                for element in lst:
                    self.tree_add_item(self.cleanse_drag_input(element))
            else:
                self.tree_add_item(self.cleanse_drag_input(data))
            if context.action == gtk.gdk.ACTION_MOVE:
                context.finish(True, True, etime)
            return

        ## Shred !!!
        def do_shred(self, widget, data=None):
            self.ttlcount = len(self.liststore)
            self.disable_widgets() #requires updating
            for element in self.liststore:
                filename = str(element[0])
                iter_num = self.settings.get_shred_iterations()
                is_zero = self.settings.is_zero()
                is_remove = self.settings.is_remove_shredded()
                ## Check if the iteration is a digit number, if not treat as invalid iterations
                if iter_num > 0:
                    # Proceed shredding operations
                    target = shreddable(filename, iter_num, is_zero, is_remove, self)
                    target.destroy()
                    # Remove shredded row
                    self.liststore.remove(element.iter)
                else:
                    iter_warn_msg = "Iteration field only accepts positive integer numbers.\nPlease try again."
                    self.dialog = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, iter_warn_msg)
                    self.dialog.run()
                    self.dialog.destroy()
            self.enable_widgets() #requires updating
            self.set_general_status("Shredding completed. " + str(self.count) + " / " + str(self.ttlcount) + ".")
            self.count = 0 # Reset count to 0 for next shredding operations.
            self.ttlcount = 0 # Reset total count to 0 for next shredding operations.


        def on_drag_data_received(widget, context, x, y, selection, target_type, timestamp):
            if target_type == 80:
                uri = selection.data.strip('\r\n\x00')
                uri_splitted = uri.split() # we may have more than one file dropped
                for uri in uri_splitted:
                    path = get_file_path_from_dnd_dropped_uri(uri)
                    widget.set_text(path)
                
        def cleanse_drag_input(self, uri):
            ## get the path to file
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

        ## Cleanse tree of duplicated items.
        def is_duplicate_tree_item(self, item):
            for element in self.liststore:
                if str(element[0]) == str(item):
                    return True
            return False

        ## Clears a selected item from tree
        def clear_selected(self, button):
            selection = self.tree.get_selection()
            model, iter = selection.get_selected()
            if iter:
                model.remove(iter)

        ## Clears the entire tree
        def clear_treeview(self, button):
            self.liststore.clear()

        #add a generic item to the list
        def tree_add_item(self, item):
            if self.is_duplicate_tree_item(item) == False:
                if not item  == "":
                    self.liststore.append([item])

        def do_save_prefs(self, widget, data=None):
            self.settings.set_shred_iterations(self.check_iterations.get_value())
            self.settings.set_remove_shredded(self.remove.get_active())
            self.settings.set_zero(self.zero.get_active())
            self.settings.commit()
