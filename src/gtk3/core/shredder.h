#ifndef CORE_SHREDDER_H
#define CORE_SHREDDER_H

#include <glib.h>

//enumeration for the ListStore
enum {COL_NAME, COL_PIXBUF, COL_URI};

//preferences struct for passing to stuff.
struct prefs {
    guint passes;
    gboolean remove;
    gboolean dnd;
    gboolean scroll;
};

#endif
