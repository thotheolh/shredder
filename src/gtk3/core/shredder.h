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

struct App {
        GtkBuilder *builder;
        GtkListStore *file_list;
        GtkIconTheme *icon_theme;
        struct prefs all_pref;
        GtkWidget *progress_window, *progress_bar, *progress_label, *about, *backend_remove, *backend_passes, *application_dnd, *application_scrollv, *application_scrollh, *shredder_window, *preferences_window, *icon_view;
};

#endif
