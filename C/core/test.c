#include "preferences.h"

void shred(const char* filename, struct preferences* prefs); 


int main() {
	struct preferences prefs;
	prefs.remove = 0;
	prefs.passes = 4;
	
	shred("test.jpg", &prefs);
}

