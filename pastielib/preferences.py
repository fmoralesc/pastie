#!/usr/bin/env python

import gtk
import gconf

GCONF_ROOT = '/apps/pastie/prefs'

class PrefsGConfClient(object):
	def __init__(self):
		self.gconf_client = gconf.client_get_default()
		self.gconf_client.add_dir(GCONF_ROOT, gconf.CLIENT_PRELOAD_NONE)

	def notify_add(self, key, callback):
		self.gconf_client.notify_add(GCONF_ROOT + '/' + key, callback)

	def get_show_quit(self):
		return self.gconf_client.get_bool(GCONF_ROOT  + '/show_quit_on_menu')

	def set_show_quit(self, value):
		self.gconf_client.set_bool(GCONF_ROOT + '/show_quit_on_menu', value)

	def get_history_size(self):
		return self.gconf_client.get_int(GCONF_ROOT + '/history_size')

	def set_history_size(self, value):
		self.gconf_client.set_int(GCONF_ROOT + '/history_size', value)

	def get_item_length(self):
		return self.gconf_client.get_int(GCONF_ROOT + '/item_length')

	def set_item_length(self, value):
		self.gconf_client.set_int(GCONF_ROOT + '/item_length', value)

class PreferencesDialog():
	def __init__(self):
		self.gconf_client = PrefsGConfClient()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(_("Pastie preferences"))
		self.window.set_resizable(False)
		self.window.set_skip_pager_hint(True)
		self.window.set_skip_taskbar_hint(True)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_border_width(12)

		vbox = gtk.VBox(spacing=6)
		self.window.add(vbox)

		prefs_box = gtk.VBox()

		main_prefs_box = gtk.VBox()
		main_prefs_box.set_size_request(300, 70)

		hist_size_pref_box = gtk.HBox()
		hist_size_pref_align = gtk.Alignment(xalign=0.0, yalign=0.5)
		hist_size_pref_label = gtk.Label(_("History size"))
		hist_size_pref_align.add(hist_size_pref_label)
		hist_size_pref_box.pack_start(hist_size_pref_align)
				
		self.hist_size_pref_spin = gtk.SpinButton(gtk.Adjustment(lower=1.0, upper=100.0, step_incr=1.0))
		self.hist_size_pref_spin.set_value(self.gconf_client.get_history_size())
		self.hist_size_pref_spin.connect("value-changed", self.change_history_size)
		hist_size_pref_box.pack_end(self.hist_size_pref_spin, expand=False)
		
		main_prefs_box.pack_start(hist_size_pref_box)

		item_length_pref_box = gtk.HBox()
		item_length_pref_align = gtk.Alignment(xalign=0.0, yalign=0.5)
		item_length_pref_label = gtk.Label(_("Menu history entries length"))
		item_length_pref_align.add(item_length_pref_label)
		item_length_pref_box.pack_start(item_length_pref_align)
			
		self.item_length_pref_spin = gtk.SpinButton(gtk.Adjustment(lower=20.0, upper=60.0, step_incr=1.0))
		self.item_length_pref_spin.set_value(self.gconf_client.get_item_length())
		self.item_length_pref_spin.connect("value-changed", self.change_item_length)
		item_length_pref_box.pack_end(self.item_length_pref_spin, expand=False)

		main_prefs_box.pack_start(item_length_pref_box)

		prefs_box.pack_start(main_prefs_box)

		misc_pref_expander = gtk.Expander(_("Misc"))

		show_misc_checkbutton = gtk.CheckButton(_("Show 'quit' on menu"))
		if self.gconf_client.get_show_quit() == True:
			show_misc_checkbutton.set_active(True)
		else:
			show_misc_checkbutton.set_active(False)
		show_misc_checkbutton.connect("toggled", self.toggle_show_quit)
		misc_pref_expander.add(show_misc_checkbutton)

		prefs_box.pack_start(misc_pref_expander)

		vbox.pack_start(prefs_box)

		self.window.show_all()
		self.window.show()

	def toggle_show_quit(self, event):
		if self.gconf_client.get_show_quit() == True:
			self.gconf_client.set_show_quit(0)
		else:
			self.gconf_client.set_show_quit(1)

	def change_history_size(self, event):
		self.gconf_client.set_history_size(int(self.hist_size_pref_spin.get_value()))

	def change_item_length(self, event):
		self.gconf_client.set_item_length(int(self.item_length_pref_spin.get_value()))

if __name__ == "__main__":
	w = PreferencesDialog()
	w.window.connect("destroy", lambda q: gtk.main_quit())
	gtk.main()
