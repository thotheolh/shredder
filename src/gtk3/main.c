#include <gtk/gtk.h>
#include <string.h>
#include <stdlib.h>
#include "core/shredder.h"
#include "core/util.h"

//message string for progress dialog
gchar* progress_status;
//percentage done. 
gdouble progress_proportion;
//files left
guint files_left;

//builder object
GtkBuilder* builder;
//main store for all shred items.
GtkListStore* file_list;
//the default icon theme
GtkIconTheme* icon_theme;
//global preferences
struct prefs all_pref = {3, FALSE};
//progressbar
GtkProgressBar* progress_bar;

//shred forward declaration
void shred_all(struct prefs* in_pref);

//show the about dialog-dialog is always existent, just usually hidden
void on_about_show() {
    gtk_widget_show_all(GTK_WIDGET(gtk_builder_get_object(builder, "about")));
}

//hide it again.
void on_about_hide() {
    gtk_widget_hide(GTK_WIDGET(gtk_builder_get_object(builder, "about")));
}

//on using menu to add wastebasket
void on_trash() {
    gchar* trash = g_strjoin(NULL, g_getenv("HOME"), "/.local/share/Trash/files", NULL);
    
    //insert values
    gtk_list_store_insert_with_values(file_list, NULL, -1,
                                COL_NAME, "Trash",
                                COL_PIXBUF, gtk_icon_theme_load_icon(icon_theme, "user-trash", 48, 0, NULL),
                                COL_URI, trash,
                                -1);
                                
    g_free(trash);
}

//on using the menu to open a file
void on_open() {
	//new dialog for file choosing
	GtkFileChooser* dialog = GTK_FILE_CHOOSER(gtk_file_chooser_dialog_new("Add file", NULL, GTK_FILE_CHOOSER_ACTION_OPEN,
											GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
											GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT,
											NULL));
                                            
    //if we don't cancel
	if(gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
        
        //insert values
        gtk_list_store_insert_with_values(file_list, NULL, -1,
                                    COL_NAME, get_name_from_uri(gtk_file_chooser_get_filename(dialog)),
                                    COL_PIXBUF, get_icon_from_filename(gtk_file_chooser_get_filename(dialog), icon_theme),
                                    COL_URI, gtk_file_chooser_get_filename(dialog),
                                    -1);
    }
    //destroy after use (very Bond!)
    gtk_widget_destroy(GTK_WIDGET(dialog));
}

//on using the menu to open a folder
void on_open_folder() {
	//new dialog for file choosing
	GtkFileChooser* dialog = GTK_FILE_CHOOSER(gtk_file_chooser_dialog_new("Add file", NULL, GTK_FILE_CHOOSER_ACTION_SELECT_FOLDER,
											GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
											GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT,
											NULL));
                                            
    //if we don't cancel
	if(gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
        
        //insert values
        gtk_list_store_insert_with_values(file_list, NULL, -1,
                                    COL_NAME, get_name_from_uri(gtk_file_chooser_get_filename(dialog)),
                                    COL_PIXBUF, gtk_icon_theme_load_icon(icon_theme, "folder", 48, 0, NULL),
                                    COL_URI, gtk_file_chooser_get_filename(dialog),
                                    -1);
    }
    //destroy after use (very Bond!)
    gtk_widget_destroy(GTK_WIDGET(dialog));
}

//un-hide the preferences dialog
void on_preferences() {
	//set according to preferences
	gtk_switch_set_active(GTK_SWITCH(gtk_builder_get_object(builder, "preferences_window_backend_remove")), all_pref.remove);
	gtk_range_set_value(GTK_RANGE(gtk_builder_get_object(builder, "preferences_window_backend_passes")), all_pref.passes);
    gtk_widget_show_all(GTK_WIDGET(gtk_builder_get_object(builder, "preferences_window")));
}

//hide preferences again
void on_preferences_hide() {
	//save configuration
	all_pref.remove = gtk_switch_get_active(GTK_SWITCH(gtk_builder_get_object(builder, "preferences_window_backend_remove")));
	all_pref.passes = gtk_range_get_value(GTK_RANGE(gtk_builder_get_object(builder, "preferences_window_backend_passes")));
	gtk_widget_hide(GTK_WIDGET(gtk_builder_get_object(builder, "preferences_window")));
}

//remove all items currently in view
void on_clear() {
    gtk_list_store_clear(file_list);
}

void on_drop(GtkWidget* icon_view, GdkDragContext *drag_context, int x, int y, GtkSelectionData* data, int info, int time, gpointer in_file_list) {
	
	gchar** split_uris_with_protocol = gtk_selection_data_get_uris(data);
	
    
    //e.g. [file:///home/bob/test], ---> [file:///home/bob/test2], --->| [\0]
	while(*split_uris_with_protocol != NULL) {
		//e.g. /home/bob/test
		gchar* uri = g_filename_from_uri(*split_uris_with_protocol, NULL, NULL);
		//e.g. test
		gchar* filename = get_name_from_uri(uri);

		//insert values
		gtk_list_store_insert_with_values(file_list, NULL, -1,
                                COL_NAME, filename,
                                COL_PIXBUF, get_icon_from_filename(uri, icon_theme),
                                COL_URI, uri,
                                -1);
        split_uris_with_protocol++;
    }
    
	//finish the drag                            
    gtk_drag_finish(drag_context, TRUE, FALSE, time);
}

//hide the progress box for reuse
void on_progress_hide() {
    gtk_widget_hide(GTK_WIDGET(gtk_builder_get_object(builder, "progress_window")));
}

//every so often, update this.
gboolean check_dialog() {
    //set progressbar
    gtk_progress_bar_set_fraction(progress_bar, progress_proportion);
    //set text from the status
    gtk_progress_bar_set_text(progress_bar, progress_status);
    //set files remaining field.
    gtk_label_set_text(GTK_LABEL(gtk_builder_get_object(builder, "progress_window_files_var")), g_strdup_printf("%i", files_left)); 
    
    //when done..
    if(progress_proportion == 1) {
        //Hide the progressbox.
        on_progress_hide();
        //clear the view
        on_clear();
        //we're done here, unqueue us from the stack.
        return FALSE;
    }
    return TRUE;
}

void on_shred() {
    //while we count up files, etc.
    progress_status = "Starting...";
    //reset bar
    progress_proportion = 0;
    //show the progress window
    gtk_widget_show_all(GTK_WIDGET(gtk_builder_get_object(builder, "progress_window")));
    //Periodically update the progress window, when we have some spare CPU time.
    g_idle_add((gpointer)(check_dialog), NULL);
    //spawn worker thread to do work for us. Commmunicates through global variables.
    g_thread_new("shredding", (gpointer)(shred_all), &all_pref);
}

//kill the mainloop
void on_quit() {
    g_message("Bye!");
    gtk_main_quit();
}

int main(int argc, char** argv) {
    //start Gtk+
    gtk_init(&argc, &argv);
    
    //intialise file list for use.
    file_list = gtk_list_store_new(3, G_TYPE_STRING, GDK_TYPE_PIXBUF, G_TYPE_STRING);
    
    //initialise the XML loader
    builder = gtk_builder_new();
    //add XML to loader
    gtk_builder_add_from_file(builder, "shredder.ui", NULL);
    //load signals from loader
    gtk_builder_connect_signals(builder, NULL);
    
    //load iconview from XML
    GtkIconView* icon_view = GTK_ICON_VIEW(gtk_builder_get_object(builder, "icon_view"));
	gtk_icon_view_set_model(icon_view, GTK_TREE_MODEL(file_list)); 
	gtk_icon_view_set_text_column (icon_view, COL_NAME);
	gtk_icon_view_set_pixbuf_column (icon_view, COL_PIXBUF);
    
    //load progressbar from XML
    progress_bar = GTK_PROGRESS_BAR(gtk_builder_get_object(builder, "progress_window_bar"));
    
    //enable DnD.
    gtk_icon_view_enable_model_drag_dest(icon_view, gtk_target_entry_new("text/uri-list", 0, 0), 1, GDK_ACTION_COPY);
    g_signal_connect(icon_view, "drag-data-received", G_CALLBACK (on_drop), file_list);
    
    //load icon theme
    icon_theme = gtk_icon_theme_get_default();
    
    //load preferences
    all_pref = load_preferences(); 
    
    //show main window
    GtkWindow* shredder_window = GTK_WINDOW(gtk_builder_get_object(builder, "shredder_window"));
    gtk_widget_show_all(GTK_WIDGET(shredder_window));
    
    //loop until quit
    gtk_main();
    
    //write config to disk
    save_preferences(&all_pref);
    
    //die.
    return 0;
}
