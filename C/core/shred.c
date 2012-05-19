//Needed, to quote the unity devs, "for ungodly stupid reasons". 
#define _XOPEN_SOURCE 500

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/stat.h>
#include <ftw.h>
#include <gtk/gtk.h>

#include "preferences.h"

//1KB buffer-big enough to be efficient, but not big enough to become a memory hog.
#define BUFFER_SIZE 1024

struct preferences* prefs;

void error(const char* message);
void warning(const char* message);

void file_shred(const char* filename) {
	FILE* file = fopen(filename, "r+");
	
	//uh-oh.
	if(file == NULL) {
		error("Could not open file for writing");
		return;
	}
	
	//no buffering, thankyou.
	setbuf(file, NULL);
	
	
	//how big is the file? Well, go to the end, then tell me how far you are away. 
	//That's C for you.
	fseek(file, 0, SEEK_END);
	int file_size = ftell(file);
	if(file_size == 0) {
		warning("Zero-byte file: ");
		//nothing to do.
		return;
	}
	
	//go back to the start to prepare for writing.
	fseek(file, 0, SEEK_SET);
	
	//allocate X bytes of memory off the stack.
	unsigned char* buffer = (unsigned char*)malloc(BUFFER_SIZE * sizeof(unsigned char));
	
	//uh-oh-very big file or some sort of other failure.
	if(buffer == NULL) {
		error("Failed to allocate memory! <this is very bad>");
		fclose(file);
		free(buffer);
		return;
	}
	
	for(int j = 0; j < prefs->passes; j++) {
		for(int i = 0; i < 2; i++) {
			//where are we?
			int position = 0;
		
			fseek(file, 0, SEEK_SET);
		
			//initialise buffer with random stuff.
			for(int x = 0; x < (BUFFER_SIZE * sizeof(unsigned char)); x++) {
				//pass 0: random. pass1: 1. pass 2: 0.
				switch(i){
					case 0:
						//re-randomise from rand()
						srand((unsigned int)rand());
						buffer[x] = (unsigned char)(rand() % (255 + 1));
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
			
				//if we're still in business
				if(position + BUFFER_SIZE <= file_size) {
					fwrite(buffer, sizeof(unsigned char), BUFFER_SIZE, file);
				
					//update our position
					position += BUFFER_SIZE;
				}
			
				//otherwise, write what's left over.
				else {
					fwrite(buffer, sizeof(unsigned char), (file_size - position), file);
				
					//we're now at EOF and can break from loop.
					position = file_size;
				}
			}
		}
	}
	
	//free the buffer.
	free(buffer);
	
	//close the file
	fclose(file);
	
	//if we're meant to remove the file...
	if(prefs->remove == 1) {
		int i = remove(filename);
		if(i < 0) warning("Could not remove file.");
	}
} 

//have we got a dir?
int is_dir(const char* filename) {
	struct stat result;
	
	//uh-oh
	if(stat(filename, &result) == -1){
		printf("Could not stat file: %s\n", filename);
		return -2;
	}
	
	//handy macro, this. Returns 1 if true, 0 if false.
	return S_ISDIR(result.st_mode);
}

//callback function for ftw() 
int shred_callback(const char* filename, const struct stat* result, int info, struct FTW* more_info) {
	if(info == FTW_F) {
		printf("%s\n", filename);
		file_shred(filename);	
	}
	return 0;
}

void shred(const char* filename, struct preferences* in_prefs) {
	
	prefs = in_prefs;
	
	switch(is_dir(filename)) {
		
		//there's been an error
		case (-2): {
			return;
			break;
		}
			
		case (0): {
			printf("File: %s\n", filename);
			file_shred(filename);
			break;
		}
			
		case (1): {
			printf("Dir: %s\n", filename);
			int flags = 0;
			flags |= FTW_PHYS;
			nftw(filename, shred_callback, 20, flags);
			break;
		}
			
		default: {
			return;
			break;
		}
			
	}
}
	
	
	
