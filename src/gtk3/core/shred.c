//needed, to quote the unity devs, for ungodly stupid reasons
#define _XOPEN_SOURCE 500

#include <glib.h>
#include <glib/gstdio.h>
#include <gtk/gtk.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ftw.h>

#include "shredder.h"
#include "util.h"

#define BUFFER_SIZE 1024
gfloat total_files = 0;
gfloat current_total = 0;

extern gdouble progress_proportion;
extern gchar* progress_status;
extern guint files_left;
extern gboolean aborted;

extern struct App app;

//Low-level file shredding. Deals with individual files
void shred_single_file(const gchar* filename)
{

    FILE *file = load_file(filename);
    if(!file) {
        return;
    }
    //set buffering to zero, theoreticallly maximising scrubbing.
    setbuf(file, NULL);

    //how big is the file? Well, go to the end, then tell me how far you are away.
    //That's C for you.
    fseek(file, 0, SEEK_END);
    int file_size = ftell(file);
    if(file_size == 0) {
        g_warning("Zero-byte file: %s", filename);
        //nothing to do.
        return;
    }

    //go back to the start to prepare for writing.
    fseek(file, 0, SEEK_SET);

    //allocate X bytes of memory off the stack.
    guchar* buffer = (guchar*)g_malloc(BUFFER_SIZE * sizeof(guchar));

    //uh-oh. This is bad, since when was 1KB of RAM a big request?
    if(!buffer)
        g_error("Failed to allocate memory...Houston, we have a problem!");

    //iterate over passes
    for(guint j = 0; j < app.all_pref.passes; j++) {
        //iterate over random, 1, 0.
        for(guint8 i = 0; i < 2; i++) {
            //where are we?
            guint64 position = 0;

            //reset file
            fseek(file, 0, SEEK_SET);

            //initialise buffer
            for(guint x = 0; x < (BUFFER_SIZE * sizeof(guchar)); x++) {
                //pass 0: random. pass1: TRUE. pass 2: FALSE.
                switch(i) {
                case 0:
                    //re-randomise from rand()
                    srand((guint)rand());
                    buffer[x] = (guchar)(rand() % (255 + 1));
                    break;

                case 1:
                    //ASCII 255, or '11111111'. :D
                    buffer[x] = '\377';

                case 2:
                    //ASCII 000, or '00000000'. :D
                    buffer[x] = '\000';
                }
            }
            //while we're not at EOF
            while(position < file_size) {
                //if we're still > BUFFER_SIZE away from EOF:
                if(position + BUFFER_SIZE <= file_size) {
                    fwrite(buffer, sizeof(guchar), BUFFER_SIZE, file);

                    //update our position
                    position += BUFFER_SIZE;
                }

                //do the bits remaining
                else {
                    fwrite(buffer, sizeof(guchar), (file_size - position), file);

                    //we're now at EOF and can break from loop.
                    position = file_size;
                }
            }
        }
    }
    //close file
    fclose(file);
    //remove if necessary
    if(app.all_pref.remove) {
        g_unlink(filename);
    }
    //free() malloc'd memory
    g_free(buffer);
}

//simple callback to increment the number of files
int count_callback(const gchar* filename, const struct stat* result, gint info, struct FTW* more_info)
{
    total_files++;
    return 0;
}

//simple callback to shred files
int shred_callback(const gchar* filename, const struct stat* result, gint info, struct FTW* more_info)
{
	if(aborted == TRUE) g_thread_exit(NULL);
    //set information...
    progress_status = g_path_get_basename(filename);
    //shreddit!
    if (info == FTW_F) shred_single_file(filename);
    //...and update the total.
    current_total++;
    //recalculate as necessary:
    progress_proportion = current_total/total_files;
    files_left = total_files - current_total;
    return 0;
}

//function to get the total number of files
void get_total()
{
	total_files = 0;
	current_total = 0;
    GtkTreeIter iter;
    //get first value, or a problem if there isn't one.
    gboolean valid = gtk_tree_model_get_iter_first(GTK_TREE_MODEL(app.file_list), &iter);
    gchar* filename;

    while(valid) {
        //get the next value
        gtk_tree_model_get(GTK_TREE_MODEL(app.file_list), &iter, COL_URI, &filename, -1);
        //if it's a directory...
        if(g_file_test(filename, G_FILE_TEST_IS_DIR)) {
            //setup ftw...
            gint ftw_flags = 0;
            ftw_flags |= FTW_PHYS;
            //iterate over files, increasing filecount.
            nftw(filename, count_callback, 20, ftw_flags);
        }
        //otherwise, just increase the filecount.
        else {
            total_files++;
        }
        //point to next set of values
        valid = gtk_tree_model_iter_next(GTK_TREE_MODEL(app.file_list), &iter);
    }

}


void shred_all()
{
    //get the total number of files, for the progressbar.
    get_total(app.file_list);

    //now, start work.
    GtkTreeIter iter;
    //get first value, or a problem if there isn't one.
    gboolean valid = gtk_tree_model_get_iter_first(GTK_TREE_MODEL(app.file_list), &iter);
    gchar* filename;

    while(valid) {
        //get the next value
        gtk_tree_model_get(GTK_TREE_MODEL(app.file_list), &iter, COL_URI, &filename, -1);
        //if it's a directory...
        if(g_file_test(filename, G_FILE_TEST_IS_DIR)) {
            //setup ftw...
            gint ftw_flags = 0;
            ftw_flags |= FTW_PHYS;
            //iterate over files, shredding as we go.
            nftw(filename, shred_callback, 20, ftw_flags);
            //remove if necessary
            if(app.all_pref.remove) {
                g_remove(filename);
            }
        }
        //otherwise, just shred the file.
        else {
            //set status
            progress_status = filename;
            //shreddit!
            shred_single_file(filename);
            //remove if necessary
            if(app.all_pref.remove) {
                g_remove(filename);
            }
            //increment 'done' pile.
            current_total++;
            //recalculate
            progress_proportion = current_total/total_files;
            files_left = total_files - current_total;
        }
        //point to next set of values
        valid = gtk_tree_model_iter_next(GTK_TREE_MODEL(app.file_list), &iter);
    }
    g_message("Complete.");
}
