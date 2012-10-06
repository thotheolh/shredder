CC=gcc
CFLAGS=-export-dynamic `pkg-config --cflags --libs gtk+-3.0` -Wall --std=c99 -ggdb
OBJECTS=src/shred.o src/util.o src/main.o 
NAME=shredder

make: $(OBJECTS)
	$(CC) $(OBJECTS) $(CFLAGS) -o $(NAME) 

clean: 
	rm -f $(OBJECTS) $(NAME)

install: make
	mkdir -p $(DESTDIR)/usr/share/shredder/
	install --mode=555 $(NAME) $(DESDIR)/usr/share/shredder/$(NAME)
	install --mode=444 shredder.ui $(DESTDIR)/usr/share/shredder/shredder.ui
	install --mode=555 data/shredder.desktop $(DESTDIR)/usr/share/applications/
	install --mode=555 src/wrapper.sh $(DESTDIR)/usr/bin/shredder
	install --mode=644 data/shredder.1.gz $(DESTDIR)/usr/share/man/man1/shredder.1.gz
	install --mode=444 data/LICENSE.html $(DESTDIR)/usr/share/shredder/
	install --mode=444 README $(DESTDIR)/usr/share/shredder/

uninstall:
	rm -rf $(DESTDIR)/usr/share/shredder /usr/bin/shredder /usr/share/applications/shredder.desktop /usr/share/man/man1/shredder.1.gz	

.PHONY: clean uninstall
