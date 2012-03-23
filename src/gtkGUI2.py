#!/usr/bin/python

import sys
import os
import urllib
from shreddable import shreddable

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
    
target = shreddable()

if importStatus:

    class gtkGUI():

        output = None
        filenametf = None
        chooser = None
        dnd_list = [ ( 'text/uri-list', 0, 80 ) ]
        cwd = os.getcwd()

        def __init__(self):
            print "Starting GTK Interface"
            self.startGUI()

        def startGUI(self):
            print "GUI Started"
            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.window.set_title("Shredder - v0.1 (Beta2)")
            self.window.set_border_width(10)
            self.window.connect("destroy", self.destroy)
            self.window.set_icon_from_file(get_resource("img/shredder256.png"))

            ## Labels
            self.filelbl = gtk.Label("File / Folder: ")
            self.iterationlbl = gtk.Label("Shred Iterations: ")
            self.zerolbl = gtk.Label("Zero-ing: ")
            self.removelbl = gtk.Label("Remove: ")

            ## Buttons
            self.shredbtn = gtk.Button()
            self.shredbtn.connect("clicked", self.do_shred, None)
            self.filechoosebtn = gtk.Button()
            self.filechoosebtn.connect("clicked", self.get_filechooser_callback, None)
            self.folderchoosebtn = gtk.Button()
            self.folderchoosebtn.connect("clicked", self.get_folderchooser_callback, None)
            self.trashbtn = gtk.Button()
            self.trashbtn.connect("clicked", self.get_trash_callback, None)

            ## Button Icons

            # Shred button
            self.shredimg = gtk.Image()
            self.shredimg.set_from_file(get_resource("img/shred.png"))
            self.shredbtn.add(self.shredimg)
            
            # File chooser button
            self.fileimg = gtk.Image()
            self.fileimg.set_from_file(get_resource("img/file.png"))
            self.filechoosebtn.add(self.fileimg)

            # Folder chooser button

            self.folderimg = gtk.Image()
            self.folderimg.set_from_file(get_resource("img/folder.png"))
            self.folderchoosebtn.add(self.folderimg)

            # Trash button

            self.trashimg = gtk.Image()
            self.trashimg.set_from_file(get_resource("img/trash.png"))
            self.trashbtn.add(self.trashimg)

            ## Check Boxes
            self.zero = gtk.CheckButton(label=None)
            self.zero.set_active(True)
            self.remove = gtk.CheckButton(label=None)
            self.remove.set_active(False)

            ## Text Fields
            self.filenametf = gtk.Entry(max=0)
            self.filenametf.connect("drag_data_received", on_drag_data_received)
            self.filenametf.drag_dest_set( gtk.DEST_DEFAULT_MOTION |
                  gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                  self.dnd_list, gtk.gdk.ACTION_COPY)
            self.itertf = gtk.Entry(max=0)
            self.itertf.set_width_chars(8)
            self.itertf.set_text("5")

            ## Text View with frame wrapping
            self.page_size = gtk.Adjustment(lower=100, page_size=100)
            self.sw = gtk.ScrolledWindow(self.page_size)
            self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            self.output = gtk.TextView()
            self.output.set_wrap_mode(gtk.WRAP_WORD)
            self.output.set_editable(False)
            self.sw.add(self.output)
            self.frame = gtk.Frame()
            self.frame.set_label(" Status: ")
            self.frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
            self.frame.add(self.sw)

            ## Tooltip Text

            # Shred button
            self.shredtooltip = gtk.Tooltips()
            self.shredtooltip.set_tip(self.shredbtn, _("Begin Shredding Files"))

            # File choose button
            self.filetooltip = gtk.Tooltips()
            self.filetooltip.set_tip(self.filechoosebtn, _("Choose a file"))

            # Folder choose button
            self.foldertooltip = gtk.Tooltips()
            self.foldertooltip.set_tip(self.folderchoosebtn, _("Choose a folder"))

            # Trash button
            self.trashtooltip = gtk.Tooltips()
            self.trashtooltip.set_tip(self.trashbtn, _("Shred Trash bin"))

            # Zero-ing checkbox
            self.zerotooltip = gtk.Tooltips()
            self.zerotooltip.set_tip(self.zero, _("Zero files when shredding"))
            self.zerolbltooltip = gtk.Tooltips()
            self.zerolbltooltip.set_tip(self.zerolbl, _("Zero files when shredding"))

            # Remove checkbox
            self.removetooltip = gtk.Tooltips()
            self.removetooltip.set_tip(self.remove, _("Remove files after shredding"))
            self.removelbltooltip = gtk.Tooltips()
            self.removelbltooltip.set_tip(self.removelbl, _("Remove files after shredding"))

            # Iteration text field
            self.itertftooltip = gtk.Tooltips()
            self.itertftooltip.set_tip(self.itertf, _("Shredding iterations per file"))

            ## Packing widgets into window

            # Vertical box to contain all boxes
            self.vbox = gtk.VBox(homogeneous=False, spacing=0)

            # filebox to contain file-based widgets
            self.filebox = gtk.HBox(homogeneous=False, spacing=0)
            self.filebox.pack_start(self.filelbl, expand=False, fill=False, padding=10)
            self.filebox.pack_start(self.filenametf, expand=False, fill=False, padding=0)
            self.filebox.pack_start(self.filechoosebtn, expand=False, fill=False, padding=10)
            self.filebox.pack_start(self.folderchoosebtn, expand=False, fill=False, padding=0)
            self.filebox.pack_start(self.trashbtn, expand=False, fill=False, padding=10)
            self.vbox.pack_start(self.filebox, expand=False, fill=False, padding=0)

            # sctrlbox to contain shred control widgets
            self.sctrlbox = gtk.HBox(homogeneous=False, spacing=0)
            self.sctrlbox.pack_start(self.iterationlbl, expand=False, fill=False, padding=10)
            self.sctrlbox.pack_start(self.itertf, expand=False, fill=False, padding=0)
            self.sctrlbox.pack_start(self.zerolbl, expand=False, fill=False, padding=10)
            self.sctrlbox.pack_start(self.zero, expand=False, fill=False, padding=0)
            self.sctrlbox.pack_start(self.removelbl, expand=False, fill=False, padding=10)
            self.sctrlbox.pack_start(self.remove, expand=False, fill=False, padding=0)
            self.vbox.pack_start(self.sctrlbox, expand=False, fill=False, padding=5)

            # Add seperator
            self.separator = gtk.HSeparator()
            self.vbox.pack_start(self.separator, expand=False, fill=False, padding=5)           

            # Output View
            self.vbox.pack_start(self.frame, expand=True, fill=True, padding=5)

            # Shred button
            self.shredbox = gtk.HBox(homogeneous=False, spacing=0)
            self.shredbox.pack_end(self.shredbtn, expand=False, fill=False, padding=5)
            self.vbox.pack_end(self.shredbox, expand=False, fill=False, padding=5)


            ## Presenting window
            self.window.add(self.vbox)
            self.window.show_all()
            gtk.main()
            return None

        def checkGtkVersion(self):
            return gtk.gtk_version
        
        def checkPyGTKVersion(self):
            return gtk.pygtk_version

        def destroy(self, widget, data=None):
            return gtk.main_quit()

        def insertText(self, text):
            if(self.output == None):
                print "Empty Output"
            else:
                self.buffer = self.output.get_buffer()
                self.buffer.insert_at_cursor(text)

        def get_trash_callback(self, widget, data=None):
            loc = os.getenv("HOME")
            self.filenametf.set_text(loc + "/.local/share/Trash")

        def get_filechooser_callback(self, widget, data=None):
            self.chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            self.chooser.set_default_response(gtk.RESPONSE_OK)
            self.chooser.set_current_folder(os.getenv("HOME"))
            response = self.chooser.run()
            if response == gtk.RESPONSE_OK:
                self.filenametf.set_text(self.chooser.get_filename())
            elif response == gtk.RESPONSE_CANCEL:
                self.chooser.destroy()
            self.chooser.destroy()

        def get_folderchooser_callback(self, widget, data=None):
            self.chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
            self.chooser.set_default_response(gtk.RESPONSE_OK)
            self.chooser.set_current_folder(os.getenv("HOME"))
            response = self.chooser.run()
            if response == gtk.RESPONSE_OK:
                self.filenametf.set_text(self.chooser.get_filename())
            elif response == gtk.RESPONSE_CANCEL:
                self.chooser.destroy()
            self.chooser.destroy()

        def disable_widgets(self):
            self.filenametf.set_sensitive(False)
            self.itertf.set_sensitive(False)
            self.filechoosebtn.set_sensitive(False)
            self.folderchoosebtn.set_sensitive(False)
            self.trashbtn.set_sensitive(False)
            self.zero.set_sensitive(False)
            self.shredbtn.set_sensitive(False)
            # self.insertText("Widgets disabled\n")

        def enable_widgets(self):
            self.filenametf.set_sensitive(True)
            self.itertf.set_sensitive(True)
            self.filechoosebtn.set_sensitive(True)
            self.folderchoosebtn.set_sensitive(True)
            self.trashbtn.set_sensitive(True)
            self.zero.set_sensitive(True)
            self.shredbtn.set_sensitive(True)
            # self.insertText("Widgets enabled\n")

        def do_shred(self, widget, data=None):
            filename = self.filenametf.get_text()
            iter_num = self.itertf.get_text()
            is_zero = self.zero.get_active()
            is_remove = self.remove.get_active()
            ## Check if the iteration is a digit number, if not treat as invalid iterations
            if iter_num.isdigit():
                if iter_num > 0:
                    # Proceed shredding operations
                    target.iterations = iter_num
                    target.filename = filename
                    target.zero = is_zero
                    target.remove = is_remove
                    target.gui = self
                    self.insertText("Target File: "+filename+"\nIterations: "+iter_num+", Zero-ing: "+str(is_zero)+", Remove: "+str(is_remove)+".\n")
                    self.insertText("Here we go! Pray that it doesn't take anything bad out!\n")
                    # Begin shredding. Widgets disabled to prevent interruption in due process.
                    self.disable_widgets()
                    target.destroy()
                    self.enable_widgets()
                    self.filenametf.set_text("")
                    # Finish shredding
                    self.insertText("Done with all the shredding! \nYou may proceed to exit or shred more stuff again.\n==========\n")
                else:
                    iter_warn_msg = "Iteration field only accepts positive integer numbers.\nPlease try again."
                    self.dialog = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, iter_warn_msg)
                    self.dialog.run()
                    self.dialog.destroy()
                    self.itertf.set_text("100")
            else:
                # Throws a warning dialog
                iter_warn_msg = "Iteration field only accepts positive integer numbers.\nPlease try again."
                self.dialog = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, iter_warn_msg)
                self.dialog.run()
                self.dialog.destroy()
                self.itertf.set_text("100")

    def on_drag_data_received(widget, context, x, y, selection, target_type, timestamp):
        if target_type == 80:
            uri = selection.data.strip('\r\n\x00')
            uri_splitted = uri.split() # we may have more than one file dropped
            for uri in uri_splitted:
                path = get_file_path_from_dnd_dropped_uri(uri)
                widget.set_text(path)
                
    def get_file_path_from_dnd_dropped_uri(uri):
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

    def get_resource(rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource
