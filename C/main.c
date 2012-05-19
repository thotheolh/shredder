#include <gtk/gtk.h>
#include <glib.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>

#include "core/preferences.h"

//enumeration for datatypes to the liststore
enum { COL_PATH, COL_PIXBUF, COL_URI };

//see shred.c
void shred(const char* filename, struct preferences* prefs);

//get a filename from an absolute filepath
char* strip_uri(const char* uri) {
	//find last occurence of '/'-not foolproof, but near enough.
	char* i = strrchr(uri, '/');
	//increment i to exclude the '/'
	i++;
	//return pointer to new string.
	return i;
}


//get a preview from a filepath returned by the filechooser widget-works for pics only. 
GdkPixbuf* get_preview(const char* filename) {
	//load from file
	GdkPixbuf* result = gdk_pixbuf_new_from_file_at_size(filename, 48, 48, NULL);
	
	//uh-oh
	if(result == NULL) {
		//load the default
		return gtk_icon_theme_load_icon(gtk_icon_theme_get_default(), "gtk-file", 48, 0, NULL);
	}
	//return it
	return result;
}

//callback for DND
void on_drag_data_received(GtkWidget* icon_view, GdkDragContext *drag_context, int x, int y, GtkSelectionData* data, int info, int time, gpointer file_list) {
	//get uri from DND
	char * uri = (char*)gtk_selection_data_get_data(data);
	
	//remove 7 characters: "file://"
	uri += 7;
	
	//make space for a filename of 7 less characters than uri.
	char * filename = uri - 7;
	//set it to uri without the "file://"
	sprintf(filename, "%s\n", uri);
	printf(filename, "%s\n", uri);
	
	//insert the values
	gtk_list_store_insert_with_values(file_list, NULL, -1,
		//the part shown as the filename
		COL_PATH, strip_uri(filename),
		//the image
		COL_PIXBUF, get_preview(filename),
		//filename for internal use
		COL_URI, filename,
		-1);
}

void about_dialog() {
	
	//authors-contributors, add yourselves, however small your contribution!
	const char* authors[] = {
        "Tay Thotheolh <twzgerald@gmail.com>",
        "Michael Rawson <michaelrawson76@gmail.com>",
        NULL
    };
    //an about dialog
	GtkAboutDialog* about = GTK_ABOUT_DIALOG(gtk_about_dialog_new());
	//set the logo to the system filesystem icon.
	gtk_about_dialog_set_logo(about, gtk_icon_theme_load_icon(gtk_icon_theme_get_default(), "drive-harddisk", 96, 0, NULL));
	//set the website
	gtk_about_dialog_set_website(about, "http://code.google.com/p/shredder");
	//set authors from const char* above
	gtk_about_dialog_set_authors(about, authors);
	//macro for the license
	gtk_about_dialog_set_license_type(about, GTK_LICENSE_GPL_3_0);
	//kill the dialog when done
	g_signal_connect_swapped (about, "response", G_CALLBACK (gtk_widget_destroy), about);
	//run it.
	gtk_dialog_run(GTK_DIALOG(about));
}

//callback for clearing the view
void clear_view(GtkWidget* view, gpointer data) {
	//clear the liststore passed.
	gtk_list_store_clear(data);
} 

//callback for adding trash.
void add_trash(GtkWidget* view, gpointer file_list) {
	//get the path for $HOME
	char * home_path = getenv("HOME");
	//add the usual (fixme!) path for trash files. I know of no distributions that do not have this.
	char * trash_path = "/.local/share/Trash/files";
	//concatenate the two.
	char * complete_path = malloc(strlen(home_path) + strlen(trash_path) + 1);
	strcpy(complete_path, home_path);
	strcat(complete_path, trash_path);

	//inset the values, setting the default icon for trashcan.
	gtk_list_store_insert_with_values(file_list, NULL, -1,
		COL_PATH, "Trash",
		COL_PIXBUF, gtk_icon_theme_load_icon(gtk_icon_theme_get_default(), "user-trash", 48, 0, NULL),
		COL_URI, complete_path,
		-1);
}
	
//callback for add_folder widget
void add_folder(GtkWidget* view, gpointer file_list) {
	//new dialog for folder choosing
	GtkWidget* dialog = gtk_file_chooser_dialog_new("Add file", NULL, GTK_FILE_CHOOSER_ACTION_SELECT_FOLDER,
											GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
											GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT,
											NULL);
											
	//if we don't cancel										
	if(gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
		//insert values...
		gtk_list_store_insert_with_values(file_list, NULL, -1,
		//strip_uri'd filename as the display filename
		COL_PATH, strip_uri(gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog))),
		//system folder icon as the icon
		COL_PIXBUF, gtk_icon_theme_load_icon(gtk_icon_theme_get_default(), "folder", 48, 0, NULL),
		//absolute path for internal use
		COL_URI, gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog)),
		-1);
	}
	
	//destroy the widget anyways
	gtk_widget_destroy(dialog);
}

//same as above
void add_file(GtkWidget* view, gpointer file_list) {
	//new dialog for file choosing
	GtkWidget* dialog = gtk_file_chooser_dialog_new("Add file", NULL, GTK_FILE_CHOOSER_ACTION_OPEN,
											GTK_STOCK_CANCEL, GTK_RESPONSE_CANCEL,
											GTK_STOCK_OPEN, GTK_RESPONSE_ACCEPT,
											NULL);
	
	//if we don't cancel
	if(gtk_dialog_run(GTK_DIALOG(dialog)) == GTK_RESPONSE_ACCEPT) {
		//get a preview if available
		GdkPixbuf* preview = get_preview(gtk_file_chooser_get_preview_filename(GTK_FILE_CHOOSER(dialog)));
		
		//insert values...
		gtk_list_store_insert_with_values(file_list, NULL, -1,
		//strip_uri'd filename as the display filename
		COL_PATH, strip_uri(gtk_file_chooser_get_uri(GTK_FILE_CHOOSER(dialog))),
		//the generated preview as the pixbuf
		COL_PIXBUF, preview,
		//Internal filename use
		COL_URI, gtk_file_chooser_get_filename(GTK_FILE_CHOOSER(dialog)),
		-1);
	}
	//destroy after use
	gtk_widget_destroy(dialog);
}

//threaded shred backend
void thread_shred(GtkListStore* file_list) {
	//a bar to show progress
	GtkProgressBar* bar = GTK_PROGRESS_BAR(gtk_progress_bar_new());
	//superimpose text
	gtk_progress_bar_set_show_text(bar, TRUE);
	//A label for the dialog
	GtkLabel* label = GTK_LABEL(gtk_label_new("Processing files..."));
	//box for everything.
	GtkBox* box = GTK_BOX(gtk_box_new(GTK_ORIENTATION_VERTICAL, 0));
	//pack everything
	gtk_box_pack_start(box, GTK_WIDGET(label), TRUE, TRUE, 5);
	gtk_box_pack_start(box, GTK_WIDGET(bar), FALSE, FALSE, 5);
	//main dialog window
	GtkWindow* dialog = GTK_WINDOW(gtk_window_new(GTK_WINDOW_TOPLEVEL));
	//set default size
	gtk_window_set_default_size(dialog, 240, 100);
	//prevent interaction with main window during this time
	gtk_window_set_modal(dialog, TRUE);
	//add the box to the window
	gtk_container_add(GTK_CONTAINER(dialog), GTK_WIDGET(box));
	//show everything
	gtk_widget_show_all(GTK_WIDGET(dialog));

	//iterator for the liststore
	GtkTreeIter iter;
	//while there's data...
	gboolean valid = gtk_tree_model_get_iter_first(GTK_TREE_MODEL(file_list), &iter);
	//duh...
	char * filename;
	//preferences object
	struct preferences prefs = { 4, 0};
	//while we have data
	while(valid) {
		//get data into filename from COL_URI
		gtk_tree_model_get(GTK_TREE_MODEL(file_list), &iter, COL_URI, &filename, -1);
		//pulse the progressbar
		gtk_progress_bar_pulse(bar);
		//set the current text
		gtk_progress_bar_set_text(bar, filename);
		//yay!
		shred(filename, &prefs);
		//update validity
		valid = gtk_tree_model_iter_next(GTK_TREE_MODEL(file_list), &iter);
	}
	//destroy widget
	gtk_widget_destroy(GTK_WIDGET(dialog));
	//clear list
	gtk_list_store_clear(file_list);
}
//shred callback

void on_shred(GtkWidget* view, GtkListStore* file_list) {
	//check user. No complaints now!
	GtkDialog* check_dialog = GTK_DIALOG(gtk_dialog_new_with_buttons("Confirm", NULL,
											GTK_DIALOG_MODAL,
											GTK_STOCK_OK, GTK_RESPONSE_ACCEPT,
											GTK_STOCK_CANCEL, GTK_RESPONSE_REJECT,
											NULL));
	//set default size	
	gtk_window_set_default_size(GTK_WINDOW(check_dialog), 320, 140);
	//get the area for content from the dialog box
	GtkBox* content = GTK_BOX(gtk_dialog_get_content_area(check_dialog));
	//message for the dialog
	GtkLabel* message = GTK_LABEL(gtk_label_new(NULL));
	//html markup
	gtk_label_set_markup(message, "All data will be <b>permamently</b> deleted.\nAre you sure you wish to continue?");
	//pack the label
	gtk_box_pack_start(content, GTK_WIDGET(message), TRUE, TRUE, 0);
	//show the dialog
	gtk_widget_show_all(GTK_WIDGET(check_dialog));
	
	//run it
	int result = gtk_dialog_run(GTK_DIALOG(check_dialog));
	//destroy the dialog
	gtk_widget_destroy(GTK_WIDGET(check_dialog));
	
	//if we're still good to go...
	if(result == GTK_RESPONSE_ACCEPT) {
		//make a new thread and send it to the shred functions...this prevents Gtk+ from freezing.
		pthread_t thread;
		pthread_create(&thread, NULL, (void*)thread_shred, file_list);
	}
}

//main function.
int main(int argc, char * argv[]) {
	
	//start Gtk+
	gtk_init(&argc, &argv);
	
	//the default icon theme
	GtkIconTheme* theme = gtk_icon_theme_get_default();
	
	//load a hard disk icon
	GdkPixbuf* window_icon = gtk_icon_theme_load_icon(theme, "drive-harddisk", 96, 0, NULL);
	
	//the main window
	GtkWindow* main_window = GTK_WINDOW(gtk_window_new(GTK_WINDOW_TOPLEVEL));
	//set default size
	gtk_window_set_default_size(main_window, 700, 500);
	//set title
	gtk_window_set_title(main_window, "shredder");
	//set icon
	gtk_window_set_icon(main_window, window_icon);
	//set border
	gtk_container_set_border_width(GTK_CONTAINER(main_window), 10);
	
	//main ListStore for files
	GtkListStore* file_list = gtk_list_store_new(3, G_TYPE_STRING, GDK_TYPE_PIXBUF, G_TYPE_STRING);
	
	//Menubar...
	GtkMenuBar* menu_bar = GTK_MENU_BAR(gtk_menu_bar_new());
		//File menu
		GtkMenu* menu_file = GTK_MENU(gtk_menu_new());
			//File Button
			GtkMenuItem* menu_file_file = GTK_MENU_ITEM(gtk_menu_item_new_with_label("File"));
			gtk_menu_item_set_submenu(GTK_MENU_ITEM(menu_file_file), GTK_WIDGET(menu_file));
			
			//Open files button
			GtkMenuItem* menu_file_files = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Open File"));
			gtk_menu_shell_append(GTK_MENU_SHELL(menu_file), GTK_WIDGET(menu_file_files));
			g_signal_connect(G_OBJECT(menu_file_files), "activate", G_CALLBACK(add_file), file_list);
			
			//Open folder button			
			GtkMenuItem* menu_file_folder = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Open Folder"));
			gtk_menu_shell_append(GTK_MENU_SHELL(menu_file), GTK_WIDGET(menu_file_folder));
			g_signal_connect(G_OBJECT(menu_file_folder), "activate", G_CALLBACK(add_folder), file_list);
			
			//Add trash button
			GtkMenuItem* menu_file_trash = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Add trash"));
			gtk_menu_shell_append(GTK_MENU_SHELL(menu_file), GTK_WIDGET(menu_file_trash));
			g_signal_connect(G_OBJECT(menu_file_trash), "activate", G_CALLBACK(add_trash), file_list);
			
			//Shred button
			GtkMenuItem* menu_file_shred = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Shred files"));
			gtk_menu_shell_append(GTK_MENU_SHELL(menu_file), GTK_WIDGET(menu_file_shred));
			g_signal_connect(G_OBJECT(menu_file_shred), "activate", G_CALLBACK(on_shred), file_list);			
						
			//Quit button
			GtkMenuItem* menu_file_quit = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Quit"));
			gtk_menu_shell_append(GTK_MENU_SHELL(menu_file), GTK_WIDGET(menu_file_quit));
			g_signal_connect(G_OBJECT(menu_file_quit), "activate", G_CALLBACK(gtk_main_quit), NULL);
			
		gtk_menu_shell_append(GTK_MENU_SHELL(menu_bar), GTK_WIDGET(menu_file_file));
		
		//Edit menu
		GtkMenu* menu_edit = GTK_MENU(gtk_menu_new());
			//Edit button
			GtkMenuItem* menu_edit_edit = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Edit"));
			gtk_menu_item_set_submenu(GTK_MENU_ITEM(menu_edit_edit), GTK_WIDGET(menu_edit));
			
			//Clear list button
			GtkMenuItem* menu_edit_clear = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Clear List"));
			gtk_menu_shell_append(GTK_MENU_SHELL(menu_edit), GTK_WIDGET(menu_edit_clear));
			g_signal_connect(G_OBJECT(menu_edit_clear), "activate", G_CALLBACK(clear_view), file_list);
			
		gtk_menu_shell_append(GTK_MENU_SHELL(menu_bar), GTK_WIDGET(menu_edit_edit));
		
		//Help Menu
		GtkMenu* menu_help = GTK_MENU(gtk_menu_new());
			//Help button
			GtkMenuItem* menu_help_help = GTK_MENU_ITEM(gtk_menu_item_new_with_label("Help"));
			gtk_menu_item_set_submenu(GTK_MENU_ITEM(menu_help_help), GTK_WIDGET(menu_help));
			
			//About button
			GtkMenuItem* menu_help_about = GTK_MENU_ITEM(gtk_menu_item_new_with_label("About"));
			gtk_menu_shell_append(GTK_MENU_SHELL(menu_help), GTK_WIDGET(menu_help_about));
			g_signal_connect(G_OBJECT(menu_help_about), "activate", G_CALLBACK(about_dialog), file_list);
			
		gtk_menu_shell_append(GTK_MENU_SHELL(menu_bar), GTK_WIDGET(menu_help_help));
	
	//main box, vertical, padded 5px.
	GtkBox* main_box = GTK_BOX(gtk_box_new(GTK_ORIENTATION_VERTICAL, 5));
	
	//top toolbar
	GtkToolbar* toolbar = GTK_TOOLBAR(gtk_toolbar_new());
	//set style
	gtk_toolbar_set_style(toolbar, GTK_TOOLBAR_BOTH);
	
	//Shred button
	GtkToolItem* shred_button = gtk_tool_button_new(NULL, "Shred All Files");
	//Set image
	gtk_tool_button_set_icon_name(GTK_TOOL_BUTTON(shred_button), "drive-harddisk");
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(shred_button), "Securely erase all open files");
	//connect
	g_signal_connect(shred_button, "clicked", G_CALLBACK (on_shred), file_list);
	//Open button
	GtkToolItem* open_files_button = gtk_tool_button_new_from_stock(GTK_STOCK_OPEN);
	//set label
	gtk_tool_button_set_label(GTK_TOOL_BUTTON(open_files_button), "Open File");
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(open_files_button), "Open a file for secure removal");
	//connect
	g_signal_connect(open_files_button, "clicked", G_CALLBACK (add_file), file_list);
	//Open button
	GtkToolItem* open_folder_button = gtk_tool_button_new_from_stock(GTK_STOCK_OPEN);
	//set label
	gtk_tool_button_set_label(GTK_TOOL_BUTTON(open_folder_button), "Open Folder");
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(open_folder_button), "Open a folder for secure removal");
	//connect
	g_signal_connect(open_folder_button, "clicked", G_CALLBACK (add_folder), file_list);
	//clear button
	GtkToolItem* clear_button = gtk_tool_button_new_from_stock(GTK_STOCK_CLEAR);
	//set label
	gtk_tool_button_set_label(GTK_TOOL_BUTTON(clear_button), "Clear Files");
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(clear_button), "Remove all items from list");
	//connect
	g_signal_connect(clear_button, "clicked", G_CALLBACK (clear_view), file_list);
	//trash button
	GtkToolItem* trash_button = gtk_tool_button_new(NULL, "Add Trash");
	//Set image
	gtk_tool_button_set_icon_name(GTK_TOOL_BUTTON(trash_button), "user-trash");
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(trash_button), "Add wastebasket to list");
	//connect
	g_signal_connect(trash_button, "clicked", G_CALLBACK (add_trash), file_list);
	//about button
	GtkToolItem* about_button = gtk_tool_button_new_from_stock(GTK_STOCK_ABOUT);
	//set label
	gtk_tool_button_set_label(GTK_TOOL_BUTTON(about_button), "About");
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(about_button), "About this application");
	//connect
	g_signal_connect(about_button, "clicked", G_CALLBACK (about_dialog), NULL);
	//quit button
	GtkToolItem* quit_button = gtk_tool_button_new_from_stock(GTK_STOCK_QUIT);
	//set label
	gtk_tool_button_set_label(GTK_TOOL_BUTTON(quit_button), "Quit");
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(quit_button), "Leave the application");
	//connect
	g_signal_connect(quit_button, "clicked", G_CALLBACK (gtk_main_quit), NULL);
	
	//Add buttons to toolbar
	gtk_toolbar_insert(toolbar, quit_button, 0);
	gtk_toolbar_insert(toolbar, about_button, 0);
	gtk_toolbar_insert(toolbar, trash_button, 0);
	gtk_toolbar_insert(toolbar, clear_button, 0);
	gtk_toolbar_insert(toolbar, open_folder_button, 0);
	gtk_toolbar_insert(toolbar, open_files_button, 0);
	gtk_toolbar_insert(toolbar, shred_button, 0);
	
	
	//add menu to main box
	gtk_box_pack_start(main_box, GTK_WIDGET(menu_bar), FALSE, FALSE, 0); 
	
	//separator
	GtkSeparator* separator = GTK_SEPARATOR(gtk_separator_new(GTK_ORIENTATION_HORIZONTAL));
	
	//scrolled window for file view
	GtkScrolledWindow* scroller = GTK_SCROLLED_WINDOW(gtk_scrolled_window_new(NULL, NULL));
	gtk_scrolled_window_set_policy(scroller, GTK_POLICY_NEVER, GTK_POLICY_AUTOMATIC);
	//Set tooltip
	gtk_widget_set_tooltip_text(GTK_WIDGET(scroller), "Drag and drop files here to add them");
	
	//icon view for files
	GtkIconView* file_icons = GTK_ICON_VIEW(gtk_icon_view_new_with_model(GTK_TREE_MODEL(file_list)));
	gtk_icon_view_set_model(file_icons, GTK_TREE_MODEL(file_list)); 
	gtk_icon_view_set_text_column (file_icons, COL_PATH);
	gtk_icon_view_set_pixbuf_column (file_icons, COL_PIXBUF);
	
	//Drag and Drop
	gtk_icon_view_enable_model_drag_dest(file_icons, gtk_target_entry_new("text/uri-list", 0, 0), 1, GDK_ACTION_COPY);
	g_signal_connect(file_icons, "drag-data-received", G_CALLBACK (on_drag_data_received), file_list);
	
	//add file_icons to scroller
	gtk_container_add(GTK_CONTAINER(scroller), GTK_WIDGET(file_icons));
	
	//add scrolled window to box
	gtk_box_pack_start(main_box, GTK_WIDGET(scroller), TRUE, TRUE, 0);
	
	//add separator to main box
	gtk_box_pack_start(main_box, GTK_WIDGET(separator), FALSE, FALSE, 0);
	
	//add toolbar to main box
	gtk_box_pack_start(main_box, GTK_WIDGET(toolbar), FALSE, FALSE, 0);
	
	//add box to window
	gtk_container_add(GTK_CONTAINER(main_window), GTK_WIDGET(main_box));
	
	//connect window destroy event
	g_signal_connect(main_window, "destroy", gtk_main_quit, NULL);
	//show window
	gtk_widget_show_all(GTK_WIDGET(main_window));
	//run gtk
	gtk_main();
	
	//finish when Gtk+ quits
	return 0;
}
