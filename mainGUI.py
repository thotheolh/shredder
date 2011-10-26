#!/usr/bin/python

import sys, os
from gtkGUI import *

desktop_environment = 'generic'
if os.environ.get('KDE_FULL_SESSION') == 'true':
    desktop_environment = 'kde'
    print 'Desktop is ',desktop_environment
elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
    desktop_environment = 'gnome'
    print 'Desktop is ',desktop_environment
    gtk = gtkGUI()
    gtk.startGUI()
else:
    try:
        info = getoutput('xprop -root _DT_SAVE_MODE')
        if ' = "xfce4"' in info:
            desktop_environment = 'xfce'
            print 'Desktop is ',desktop_environment
    except (OSError, RuntimeError):
        pass




