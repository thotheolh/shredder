#include <gtk/gtk.h>
#include <string.h>
#include <stdlib.h>
#include "core/shredder.h"
#include "core/util.h"
/*
 *Global variables for passing between threads
 */
//message string for progress dialog
gchar *progress_status;
//percentage done.
gdouble progress_proportion;
//files left
guint files_left;
//if we abort
gboolean aborted = FALSE;

/*
 *App struct for sharing widgets between functions.
 */

struct App app;

//shred forward declaration
void shred_all(struct prefs* in_pref);

//show the about dialog-dialog is always existent, just usually hidden
void on_about_show()
{
    gtk_widget_show_all(app.about);
}

//hide it again.
void on_about_hide()
{
    gtk_widget_hide(app.about);
}

//on using menu to add wastebasket
void on_trash()
{
    gchar* trash = g_strjoin(NULL, g_getenv("HOME"), "/.local/share/Trash/files", NULL);

    //insert values
    gtk_list_store_insert_with_values(app.file_list, NULL, -1,
                                      COL_NAME, "Trash",
                                      COL_PIXBUF, gtk_icon_theme_load_icon(app.icon_theme, "user-trash", 48, 0, NULL),
                                      COL_URI, trash,
                                      -1);

    g_free(trash);
}

//on using the menu to open a file
void on_open()
{
    //new dialog for file choosing
    GtkFileChooser* dialog = GTK_FILE_CHOOSER(gtk_file_chooser_dialog_new("Add file", NULL, GTK_FILE_CHOOSER_ACTION_OPEN,
                             GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
                             GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT,
                             NULL));

    //if we don't cancel
    if(gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {

        //insert values
        gtk_list_store_insert_with_values(app.file_list, NULL, -1,
                                          COL_NAME, g_path_get_basename(gtk_file_chooser_get_filename(dialog)),
                                          COL_PIXBUF, get_icon_from_filename(gtk_file_chooser_get_filename(dialog), app.icon_theme),
                                          COL_URI, gtk_file_chooser_get_filename(dialog),
                                          -1);
    }
    //destroy after use (very Bond!)
    gtk_widget_destroy(GTK_WIDGET(dialog));
}

//on using the menu to open a folder
void on_open_folder()
{
    //new dialog for file choosing
    GtkFileChooser* dialog = GTK_FILE_CHOOSER(gtk_file_chooser_dialog_new("Add file", NULL, GTK_FILE_CHOOSER_ACTION_SELECT_FOLDER,
                             GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
                             GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT,
                             NULL));

    //if we don't cancel
    if(gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {

        //insert values
        gtk_list_store_insert_with_values(app.file_list, NULL, -1,
                                          COL_NAME, g_path_get_basename(gtk_file_chooser_get_filename(dialog)),
                                          COL_PIXBUF, gtk_icon_theme_load_icon(app.icon_theme, "folder", 48, 0, NULL),
                                          COL_URI, gtk_file_chooser_get_filename(dialog),
                                          -1);
    }
    //destroy after use (very Bond!)
    gtk_widget_destroy(GTK_WIDGET(dialog));
}

void on_drop(GtkWidget* icon_view, GdkDragContext *drag_context, int x, int y, GtkSelectionData* data, int info, int time, gpointer in_file_list)
{

    gchar** split_uris_with_protocol = gtk_selection_data_get_uris(data);


    //e.g. [file:///home/bob/test], ---> [file:///home/bob/test2], --->| [\0]
    while(*split_uris_with_protocol != NULL) {
        //e.g. /home/bob/test
        gchar* uri = g_filename_from_uri(*split_uris_with_protocol, NULL, NULL);
        //e.g. test
        gchar* filename = g_path_get_basename(uri);

        //insert values
        gtk_list_store_insert_with_values(app.file_list, NULL, -1,
                                          COL_NAME, filename,
                                          COL_PIXBUF, get_icon_from_filename(uri, app.icon_theme),
                                          COL_URI, uri,
                                          -1);
        split_uris_with_protocol++;
    }

    //finish the drag
    gtk_drag_finish(drag_context, TRUE, FALSE, time);
}

//un-hide the preferences dialog
void on_preferences()
{
    //set according to preferences
    gtk_switch_set_active(GTK_SWITCH(app.backend_remove), app.all_pref.remove);
    gtk_switch_set_active(GTK_SWITCH(app.application_dnd), app.all_pref.dnd);
    gtk_range_set_value(GTK_RANGE(app.backend_passes), app.all_pref.passes);
    gtk_widget_show_all(app.preferences_window);
}

//hide preferences again
void on_preferences_hide()
{
    //save configuration
    app.all_pref.remove = gtk_switch_get_active(GTK_SWITCH(app.backend_remove));
    app.all_pref.passes = gtk_range_get_value(GTK_RANGE(app.backend_passes));
    app.all_pref.dnd = gtk_switch_get_active(GTK_SWITCH(app.application_dnd));
    if(app.all_pref.dnd) {
        gtk_icon_view_enable_model_drag_dest(GTK_ICON_VIEW(app.icon_view), gtk_target_entry_new("text/uri-list", 0, 0), 1, GDK_ACTION_COPY);
        g_signal_connect(app.icon_view, "drag-data-received", G_CALLBACK (on_drop), app.file_list);
    }
    else {
	gtk_icon_view_unset_model_drag_dest(GTK_ICON_VIEW(app.icon_view));
    }
    gtk_widget_hide(app.preferences_window);
}

//remove all items currently in view
void on_clear()
{
    gtk_list_store_clear(app.file_list);
}

//hide the progress box for reuse
void on_progress_hide()
{
    gtk_widget_hide(app.progress_window);
    if(progress_proportion != 1.0 && progress_proportion != 1.1) {
		aborted = TRUE;
		gtk_dialog_run(GTK_DIALOG(app.abort_dialog));
	}
	else if(progress_proportion == 1.1) {
		aborted = FALSE;
	}
	else {
		aborted = FALSE;
		gtk_dialog_run(GTK_DIALOG(app.success_dialog));
	}
}

void abort_dialog_hide() {
	gtk_widget_hide(app.abort_dialog);
}

void success_dialog_hide() {
	gtk_widget_hide(app.success_dialog);
}

//every so often, update this.
gboolean check_dialog()
{
    //set progressbar
    gtk_progress_bar_set_fraction(GTK_PROGRESS_BAR(app.progress_bar), progress_proportion);
    //set text from the status
    gtk_progress_bar_set_text(GTK_PROGRESS_BAR(app.progress_bar), progress_status);
    //set files remaining field.
    gtk_label_set_markup(GTK_LABEL(app.progress_label), g_strdup_printf("<b>%i</b>", files_left));

    //when done..
    if(progress_proportion >= 1) {
        //Hide the progressbox.
        on_progress_hide();
        //clear the view
        on_clear();
        //we're done here, unqueue us from the stack.
        return FALSE;
    }
    return TRUE;
}

void on_shred()
{
    //while we count up files, etc.
    progress_status = "Starting...";
    //reset bar
    progress_proportion = 0;
    //reset file count
    files_left = 0;
    //make sure we haven't aborted
    aborted = FALSE;
    //show the progress window
    gtk_widget_show_all(app.progress_window);
    gdk_window_set_cursor(gtk_widget_get_window(app.progress_window), app.loading_cursor);
    //Periodically update the progress window, when we have some spare CPU time.
    g_idle_add((gpointer)(check_dialog), NULL);
    //spawn worker thread to do work for us. Commmunicates through global variables.
    g_thread_new("shredding", (gpointer)(shred_all), &(app.all_pref));
}

//kill the mainloop
void on_quit()
{
    //write config to disk
    save_preferences(&(app.all_pref));
    g_message("Bye!");
    gtk_main_quit();
}

int main(int argc, char **argv)
{
    //start Gtk+
    gtk_init(&argc, &argv);

    //intialise apps struct
    app.file_list = gtk_list_store_new(3, G_TYPE_STRING, GDK_TYPE_PIXBUF, G_TYPE_STRING);
    app.all_pref = load_preferences();
    app.builder = gtk_builder_new();
    if(gtk_builder_add_from_file(app.builder, argv[1], NULL) == 0) {
        g_print("Usage:\n\n/path/to/executable /path/to/shredder.ui\n");
        exit(1);
    }
    gtk_builder_connect_signals(app.builder, NULL);
    app.icon_view = GTK_WIDGET(gtk_builder_get_object(app.builder, "icon_view"));
    gtk_icon_view_set_model(GTK_ICON_VIEW(app.icon_view), GTK_TREE_MODEL(app.file_list));
    gtk_icon_view_set_text_column(GTK_ICON_VIEW(app.icon_view), COL_NAME);
    gtk_icon_view_set_pixbuf_column(GTK_ICON_VIEW(app.icon_view), COL_PIXBUF);
    app.progress_bar = GTK_WIDGET(gtk_builder_get_object(app.builder, "progress_window_bar"));
    if(app.all_pref.dnd) {
        gtk_icon_view_enable_model_drag_dest(GTK_ICON_VIEW(app.icon_view), gtk_target_entry_new("text/uri-list", 0, 0), 1, GDK_ACTION_COPY);
        g_signal_connect(app.icon_view, "drag-data-received", G_CALLBACK (on_drop), app.file_list);
    }
    app.icon_theme = gtk_icon_theme_get_default();
    app.about = GTK_WIDGET(gtk_builder_get_object(app.builder, "about"));
    app.progress_window = GTK_WIDGET(gtk_builder_get_object(app.builder, "progress_window"));
    app.progress_bar = GTK_WIDGET(gtk_builder_get_object(app.builder, "progress_window_bar"));
    app.progress_label = GTK_WIDGET(gtk_builder_get_object(app.builder, "progress_window_files_var"));
    app.backend_remove = GTK_WIDGET(gtk_builder_get_object(app.builder, "preferences_window_backend_remove"));
    app.backend_passes = GTK_WIDGET(gtk_builder_get_object(app.builder, "preferences_window_backend_passes"));
    app.application_dnd = GTK_WIDGET(gtk_builder_get_object(app.builder, "preferences_window_application_dnd"));
    app.preferences_window = GTK_WIDGET(gtk_builder_get_object(app.builder, "preferences_window"));
    app.toolbar = GTK_WIDGET(gtk_builder_get_object(app.builder, "toolbar1"));
    app.abort_dialog = GTK_WIDGET(gtk_builder_get_object(app.builder, "abort_dialog"));
    app.success_dialog = GTK_WIDGET(gtk_builder_get_object(app.builder, "success_dialog"));
    app.loading_cursor = gdk_cursor_new(GDK_WATCH);
	GtkStyleContext *context = gtk_widget_get_style_context(app.toolbar);
	gtk_style_context_add_class(context, GTK_STYLE_CLASS_PRIMARY_TOOLBAR);
    app.shredder_window = GTK_WIDGET(gtk_builder_get_object(app.builder, "shredder_window"));
    gtk_widget_grab_focus(app.icon_view);
    gtk_widget_show_all(app.shredder_window);

    //loop until quit
    gtk_main();

    //die.
    return 0;
}
