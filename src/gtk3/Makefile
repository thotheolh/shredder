CC=gcc
CFLAGS=-export-dynamic `pkg-config --cflags --libs gtk+-3.0` -Wall --std=c99 -ggdb
OBJECTS=core/shred.o core/util.o main.o 
NAME=shredder

make: $(OBJECTS)
	$(CC) $(OBJECTS) $(CFLAGS) -o $(NAME) 

clean: 
	rm -f $(OBJECTS) $(NAME)

.PHONY: clean
