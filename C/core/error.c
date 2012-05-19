#include <stdio.h>

void warning(const char* message) {
	printf("**Warning:**");
	printf("\t%s\n", message);
}

void error(const char* message) {
	printf("***ERROR:***");
	printf("\t%s\n", message);
	printf("Terminated.\n");
}
