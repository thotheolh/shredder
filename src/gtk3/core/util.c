#include <gtk/gtk.h>
#include <glib.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <glib/gstdio.h>
#include <fcntl.h>

#include "shredder.h"

const gchar* DEFAULT_PREFS = "[Application]\ndnd=true\nscroll=true[Backend]\npasses=3\nremove=false";

FILE* load_file(const char *filename) {
	//check it
    if(!g_file_test(filename, G_FILE_TEST_EXISTS)) {
        g_critical("Non-existent file: %s", filename);
        return NULL;
    }

    if(!g_file_test(filename, G_FILE_TEST_IS_REGULAR)) {
        g_critical("Directory: %s", filename);
        return NULL;
    }
    //open the file
    FILE* file = fopen(filename, "r+");

    //double-check it.
    if(!file) {
            g_critical("Failed to open file: %s", filename);
            return NULL;
    }
	return file;
}

//return the appropiate icon. Not foolproof, FIXME.
GdkPixbuf* get_icon_from_filename(const gchar* uri, GtkIconTheme* icon_theme) {
    if(g_file_test(uri, G_FILE_TEST_IS_DIR)) return gtk_icon_theme_load_icon(icon_theme, "folder", 48, 0, NULL);
    else if(!g_file_test(uri, G_FILE_TEST_IS_DIR)) return gtk_icon_theme_load_icon(icon_theme, "gtk-file", 48, 0, NULL);
}

//make the default preferences, should there be a problem
struct prefs make_default_preferences() {
    gchar* path = g_strconcat(getenv("HOME"), "/.config/shredder", NULL);
    FILE* file = fopen(path, "w+");
    //.......................<|.....get length of string....|>
    fwrite(DEFAULT_PREFS, 1, g_utf8_strlen(DEFAULT_PREFS, -1), file);
    fclose(file);
    g_free(path);
    struct prefs pref = {3, FALSE, TRUE, TRUE};
    return pref;
}

//load preferences from file
struct prefs load_preferences() {
	//default values
    struct prefs pref;
    //blank config loader
    GKeyFile* file = g_key_file_new();
    //get config location
    gchar* config_file = g_strconcat(getenv("HOME"), "/.config/shredder", NULL);
    //if we've got a problem...
    if(!g_key_file_load_from_file(file, config_file, G_KEY_FILE_NONE, NULL)) {
        pref = make_default_preferences();
        g_warning("Error opening config file, creating default");
        //free the key file
		g_key_file_free(file);
		return pref;
    }
    //get values from the loader
    pref.passes = g_key_file_get_integer(file, "Backend", "passes", NULL);
    g_warning("%d\n", pref.passes);
    pref.remove = g_key_file_get_boolean(file, "Backend", "remove", NULL);
    g_warning("%d\n", pref.remove);
    pref.dnd = g_key_file_get_boolean(file, "Application", "dnd", NULL);
    g_warning("%d\n", pref.dnd);
    pref.scroll = g_key_file_get_boolean(file, "Application", "scroll", NULL);
    g_warning("%d\n", pref.scroll);
    
    //free the key file
    g_key_file_free(file);
    return pref;
}

void save_preferences(struct prefs* pref) {
    //blank config loader
    GKeyFile* file = g_key_file_new();
    //get config location
    gchar* config_file = g_strconcat(getenv("HOME"), "/.config/shredder", NULL);
    //assume no corruption, already dealt with earlier...FIXME?
    g_key_file_load_from_file(file, config_file, G_KEY_FILE_NONE, NULL);
	
	//set values
	g_key_file_set_boolean(file, "Application", "dnd", pref->dnd);
	g_key_file_set_boolean(file, "Application", "scroll", pref->scroll);
	g_key_file_set_integer(file, "Backend", "passes", pref->passes);
	g_key_file_set_boolean(file, "Backend", "remove", pref->remove);
	
	//write values
	gchar* data = g_key_file_to_data(file, NULL, NULL);
	g_file_set_contents(config_file, data, -1, NULL);
	g_key_file_free(file);
}

			  
		
