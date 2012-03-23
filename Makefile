EXE=shredder
FILES=src/*.py

make : $(EXE) $(FILES)

install: make
	mkdir -p $(DESTDIR)/usr/bin/
	cp $(EXE) $(DESTDIR)/usr/bin/shredder
	mkdir -p $(DESTDIR)/usr/share/pyshared/shredder/
	cp $(FILES) $(DESTDIR)/usr/share/pyshared/shredder/
	mkdir -p $(DESTDIR)/usr/share/pixmaps/
	cp src/img/shredder48.png $(DESTDIR)/usr/share/pixmaps/shredder.png
	mkdir -p $(DESTDIR)/usr/share/man/man1/
	cp data/shredder.1.gz $(DESTDIR)/usr/share/man/man1/
	mkdir -p $(DESTDIR)/usr/share/applications/
	cp data/shredder.desktop $(DESTDIR)/usr/share/applications/
	mkdir -p $(DESTDIR)/usr/share/pyshared/shredder/locale
	cp -r locale/* $(DESTDIR)/usr/share/pyshared/shredder/locale/
