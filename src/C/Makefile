CC=gcc
CFLAGS=-Wall --std=c99 -ggdb `pkg-config --cflags --libs gtk+-3.0` `pkg-config --cflags --libs glib-2.0` -lpthread
OBJECTS=core/error.o core/shred.o

make: $(OBJECTS)
	$(CC) $(OBJECTS) main.c -o shredder $(CFLAGS) 

clean: 
	rm $(OBJECTS) shredder

.PHONY: clean
