#!/usr/bin/python

import sys

tk = True

try:
    from Tkinter import *

except ImportError:
    print "Python-tk module does not exist. Can't launch GUI !"
    print "Please use terminal command: 'sudo apt-get install python-tk' to install Python-tk module."
    tk = False
if tk:

    class GUI(Frame):

    # Todo: Switch to grid layout

    # Test function
        def say_hi(self):
            print "hi there, everyone!"

        def createWidgets(self):

        # Textfield for target files/folders
        Label(self, text='Target: ').grid(row=0, column=0, sticky=W, padx=2)
        t=StringVar()
        self.del_tf = Entry(self, width=27, textvariable=t).grid(row=0, column=1)

        # Select folder button
        self.sel_folder = Button(self)
        self.sel_folder["text"] = "..."
        self.sel_folder.grid(row=0, column=2, sticky=W, padx=5, pady=5)

        # Select trash button
        self.sel_trash = Button(self)
        self.sel_trash["text"] = "Trash"
        self.sel_trash.grid(row=0, column=3	)

        # Textfield for target files/folders
        Label(self, text='Iterations: ').grid(row=1, column=0, padx=2)
        t=StringVar()
        self.iter_tf = Entry(self, width=27, textvariable=t).grid(row=1, column=1)

        # Checkbuttons for selecting Zero-ing and Random options
        self.sharedf = Frame(height=2, bd=1, relief=SUNKEN)
        
        var  = IntVar()
        self.zero_check = Checkbutton(self, text="Zero-ing", variable = var)
        self.zero_check.grid(row=1, column=2)
        var1 = IntVar()
        self.zero_check = Checkbutton(self, text="Randomize", variable = var1)
        self.zero_check.grid(row=1, column=3)

        # Reset button
        self.reset = Button(self)
        self.reset["text"] = "Reset"
        self.reset.grid(row=2, column=2, padx=5, pady=5)

        # Start shredding button
        self.start = Button(self)
        self.start["text"] = "Start"
        self.start.grid(row=2, column=3, padx=5, pady=5)

        # Status textarea
        # self.status = Text(root, height=26, width=50, wrap=WORD)
        # self.scroll = Scrollbar(self)
        # self.status.focus_set()
        # self.scroll.grid(row=3, column=0)
        # self.status.grid(row=3, column=0)
        # self.scroll.config(command=self.status.yview)
        # self.status.config(yscrollcommand=self.scroll.set)

        # Progress bar
        

        # Button for QUIT
            # self.QUIT = Button(self)
            # self.QUIT["text"] = "QUIT"
            # self.QUIT["fg"]   = "red"
            # self.QUIT["command"] =  self.quit
            # self.QUIT.pack(side=LEFT)
        
        # Button for Hello
            # self.hi_there = Button(self)
            # self.hi_there["text"] = "Hello",
            # self.hi_there["command"] = self.say_hi
            # self.hi_there.pack(side=LEFT)

        def __init__(self, master=None):
            Frame.__init__(self, master)
            self.pack()
            self.createWidgets()


    root = Tk() #Creates root window
    root.title("Shredder - Shred GUI frontend")
    window = GUI(master=root)
    root.mainloop()
