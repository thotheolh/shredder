#ifndef CORE_UTIL_H
#define CORE_UTIL_H

gchar* get_name_from_uri(const gchar* uri);
GdkPixbuf* get_icon_from_filename(const gchar* uri, GtkIconTheme* icon_theme);
struct prefs load_preferences();
void save_preferences(struct prefs* pref);

#endif
