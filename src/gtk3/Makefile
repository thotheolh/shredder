CC=gcc
CFLAGS=-export-dynamic `pkg-config --cflags --libs gtk+-3.0` -Wall --std=c99 -ggdb
OBJECTS=core/shred.o core/util.o main.o 
NAME=shredder

make: $(OBJECTS)
	$(CC) $(OBJECTS) $(CFLAGS) -o $(NAME) 

clean: 
	rm -f $(OBJECTS) $(NAME)

install: make
	mkdir -p $(DESTDIR)/usr/share/shredder/
	cp -f $(NAME) $(DESDIR)/usr/share/shredder/$(NAME)
	cp -f shredder.ui $(DESTDIR)/usr/share/shredder/shredder.ui
	ln -sf $(DESTDIR)/usr/share/shredder/$(NAME) $(DESTDIR)/usr/bin/$(NAME)
	cp -f data/48x48.png $(DESTDIR)/usr/share/icons/hicolor/48x48/apps/shredder.png
	cp -f data/drawing.svg $(DESTDIR)/usr/share/icons/hicolor/scalable/apps/shredder.svg
	cp -f data/shredder.desktop /usr/share/applications/

.PHONY: clean
