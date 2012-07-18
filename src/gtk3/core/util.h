#ifndef CORE_UTIL_H
#define CORE_UTIL_H

FILE* load_file(const char *filename);
GdkPixbuf* get_icon_from_filename(const gchar* uri, GtkIconTheme* icon_theme);
struct prefs load_preferences();
void save_preferences(struct prefs* pref);

#endif
