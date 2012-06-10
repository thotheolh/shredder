#include <gtk/gtk.h>
#include <glib.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <glib/gstdio.h>
#include <fcntl.h>

#include "shredder.h"

const gchar* DEFAULT_PREFS = "[Application]\ndnd=true\nscroll=true[Backend]\npasses=3\nremove=false";

//get a filename from a URI
gchar* get_name_from_uri(const gchar* uri) {
    //find last occurrence of '/'
    gchar* i = strrchr(uri, '/');
    //remove '/'
    i++;
    //return the filename.
    return i;
}

//return the appropiate icon. Not foolproof, FIXME.
GdkPixbuf* get_icon_from_filename(const gchar* uri, GtkIconTheme* icon_theme) {
    if(g_file_test(uri, G_FILE_TEST_IS_DIR)) return gtk_icon_theme_load_icon(icon_theme, "folder", 48, 0, NULL);
    else if(!g_file_test(uri, G_FILE_TEST_IS_DIR)) return gtk_icon_theme_load_icon(icon_theme, "gtk-file", 48, 0, NULL);
}

//make the default preferences, should there be a problem
void make_default_preferences() {
    gchar* path = g_strconcat(getenv("HOME"), "/.config/shredder", NULL);
    FILE* file = fopen(path, "w+");
    //.......................<|.....get length of string....|>
    fwrite(DEFAULT_PREFS, 1, g_utf8_strlen(DEFAULT_PREFS, -1), file);
    fclose(file);
    g_free(path);
}

//load preferences from file
struct prefs load_preferences() {
	//default values
    struct prefs pref = {3, FALSE};
    //blank config loader
    GKeyFile* file = g_key_file_new();
    //get config location
    gchar* config_file = g_strconcat(getenv("HOME"), "/.config/shredder", NULL);
    //if we've got a problem...
    if(!g_key_file_load_from_file(file, config_file, G_KEY_FILE_NONE, NULL)) {
        make_default_preferences();
        g_warning("Error opening config file, creating default");
        
    }
    //get values form the loader
    pref.passes = g_key_file_get_integer(file, "Backend", "passes", NULL);
    pref.remove = g_key_file_get_boolean(file, "Backend", "remove", NULL);
    pref.dnd = g_key_file_get_boolean(file, "Application", "dnd", NULL);
    pref.scroll = g_key_file_get_boolean(file, "Application", "scroll", NULL);
    
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
	g_key_file_set_integer(file, "Backend", "passes", pref->passes);
	g_key_file_set_boolean(file, "Backend", "remove", pref->remove);
	g_key_file_set_boolean(file, "Application", "dnd", pref->dnd);
	g_key_file_set_boolean(file, "Application", "scroll", pref->scroll);
	
	//write values
	gchar* data = g_key_file_to_data(file, NULL, NULL);
	g_file_set_contents(config_file, data, -1, NULL);
	g_key_file_free(file);
}

			  
		
