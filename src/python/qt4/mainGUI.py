#!/usr/bin/python

import sys, os

#!/usr/bin/env python

##TODO after impromptu meeting: make this cleaner, separate branches for the various toolkits

from subprocess import *

desktop_environment = 'generic'
if os.environ.get('KDE_FULL_SESSION') == 'true':
    desktop_environment = 'KDE'
    print 'Desktop is ',desktop_environment
elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
    desktop_environment = 'Gnome'
    print 'Desktop is ',desktop_environment
    proc = Popen("gnome-session --version", shell=True, stdout=PIPE) # Attempts to use "gnome-session --version" command to find out gnome version. Uses subprocess module.
    output = proc.communicate()[0]
    if output.startswith("gnome-session"):  # Checks if the returned "gnome-session --version" command starts with the "gnome-session" reply to find gnome version.
        g_version = output.lstrip("gnome-session ")
        g_version_array = g_version.split(".") # Splits version number to find the major version
        if g_version_array[0] == "2": # Major version is 2 therefore is Gnome 2
            print "Gnome version: ",g_version_array[0],"-", g_version
            from gtkGUI2 import *
            mainwin = gtkGUI2() # Runs under Gnome 2 env using gtkGUI2.py
        elif g_version_array[0] == "3": # Major version is 3 therefore is Gnome 3
            print "Gnome version:",g_version_array[0],"-", g_version
            from gtkGUI3 import *
            mainwin = UI() # Runs under Gnome 3 env using gtkGUI3.py
        else:
            print "Your Gnome version may not be valid !"
    else: # "gnome-session --version" command does not give satisfying reply starting with "gnome-session".
        print "Your Gnome version may not be valid !"
elif os.environ.get('XDG_CURRENT_DESKTOP') == 'LXDE':
    desktop_environment = 'LXDE'
    print 'Desktop is ',desktop_environment
    from gtkGUI2 import *
    mainwin = gtkGUI2() # Runs under Gnome 2 env using gtkGUI2.py
else:
    try:
        info = getoutput('xprop -root _DT_SAVE_MODE')
        if ' = "xfce4"' in info:
            desktop_environment = 'XFCE'
            print 'Desktop is ',desktop_environment
    except (OSError, RuntimeError):
        pass




