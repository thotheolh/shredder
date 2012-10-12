#!/usr/bin/make -f

all:
	rm -f *.pyc *~

install: all
	mkdir -p $(DESTDIR)/usr/share/shredder-gtk2/
	cp *.py $(DESTDIR)/usr/share/shredder-gtk2/
	cp -r img/ $(DESTDIR)/usr/share/shredder-gtk2/
	install --mode=555 wrapper.sh $(DESTDIR)/usr/bin/shredder-gtk2
	install --mode=444 data/shredder-gtk2.desktop $(DESTDIR)/usr/share/applications
