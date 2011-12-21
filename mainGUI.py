#!/usr/bin/python

import sys, os
from gtkGUI import *

desktop_environment = 'generic'
if os.environ.get('KDE_FULL_SESSION') == 'true':
    desktop_environment = 'KDE'
    print 'Desktop is ',desktop_environment
elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
    desktop_environment = 'Gnome'
    print 'Desktop is ',desktop_environment
    gtkGUI()
elif os.environ.get('XDG_CURRENT_DESKTOP') == 'LXDE':
    desktop_environment = 'LXDE'
    print 'Desktop is ',desktop_environment
    gtkGUI()
else:
    try:
        info = getoutput('xprop -root _DT_SAVE_MODE')
        if ' = "xfce4"' in info:
            desktop_environment = 'XFCE'
            print 'Desktop is ',desktop_environment
    except (OSError, RuntimeError):
        pass




