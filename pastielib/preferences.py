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

def get_pref(pref, default):
	value = gconf.client_get_default().get(GCONF_ROOT + "/" + pref)
	if value != None:
		if value.type.value_nick == 'int':
			return value.get_int()
		elif value.type.value_nick == 'bool':
			return value.get_bool()
		elif value.type.value_nick == 'string':
			return value.get_string()
	else:
		return default

def set_pref(pref, value, value_type):
	path = GCONF_ROOT + "/" + pref
	if value_type == 'bool':
		gconf.client_get_default().set_bool(path, value)
	elif value_type == 'int':
		gconf.client_get_default().set_int(path, value)
	elif value_type == 'string':
		gconf.client_get_default().set_string(path, value)

def get_use_primary():
	return get_pref('use_primary', False)

def set_use_primary(value):
	set_pref('use_primary', value, 'bool')

def get_synch_primary():
	return get_pref('synch_primary', True)

def set_synch_primary(value):
	set_pref('synch_primary', value, 'bool')

def get_show_quit():
	return get_pref('show_quit_on_menu', False)

def set_show_quit(value):
	set_pref('show_quit_on_menu', value, 'bool')

def get_show_prefs():
	return get_pref('show_preferences_on_menu', False)

def set_show_prefs(value):
	set_pref('show_preferences_on_menu', value, 'bool')

def get_history_size():
	return get_pref('history_size', 25)

def set_history_size(value):
	set_pref('history_size', value, 'int')

def get_item_length():
	return get_pref('item_length', 60)

def set_item_length(value):
	set_pref('item_length', value, 'int')

def get_prefs_dialog_key():
	return get_pref('prefs_dialog_key', "<Control><Alt>P") 

def set_prefs_dialog_key(value):
	set_pref('prefs_dialog_key', value, 'string')

def get_sel_dialog_key():
	return get_pref('sel_dialog_key', "<Control><Shift>C")

def set_sel_dialog_key(value):
	set_pref('sel_dialog_key', value, 'string')

class PreferencesDialog():
	def __init__(self):
		self.gconf_client = PrefsGConfClient()

		# toplevel window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(_("Pastie preferences"))
		self.window.set_resizable(False)
		self.window.set_skip_pager_hint(True)
		self.window.set_skip_taskbar_hint(True)
		self.window.set_position(gtk.WIN_POS_CENTER)

		# notebook
		ntbk = gtk.Notebook()
		ntbk.set_scrollable(True)
		self.window.add(ntbk)
		
		# General tab
		main_prefs_box = gtk.VBox()
		main_prefs_box.set_border_width(3)
		ntbk.append_page(main_prefs_box, gtk.Label(_("General")))

		hist_size_pref_box = gtk.HBox()
		hist_size_pref_align = gtk.Alignment(xalign=0.0, yalign=0.5)
		hist_size_pref_label = gtk.Label(_("History size"))
		hist_size_pref_align.add(hist_size_pref_label)
		hist_size_pref_box.pack_start(hist_size_pref_align)
				
		self.hist_size_pref_spin = gtk.SpinButton(gtk.Adjustment(lower=1.0, upper=100.0, step_incr=1.0))
		self.hist_size_pref_spin.set_value(get_history_size())
		self.hist_size_pref_spin.connect("value-changed", self.change_history_size)
		hist_size_pref_box.pack_end(self.hist_size_pref_spin)
		
		main_prefs_box.pack_start(hist_size_pref_box, expand=False)

		primary_frame = gtk.Frame(_("Primary selection"))
		main_prefs_box.pack_start(primary_frame)
		
		primary_box = gtk.VBox()
		primary_frame.add(primary_box)

		use_primary_checkbutton = gtk.CheckButton(_("Use primary selection"))
		if get_use_primary() == True:
			use_primary_checkbutton.set_active(True)
		else:
			use_primary_checkbutton.set_active(False)
		use_primary_checkbutton.connect("toggled", self.toggle_use_primary)
		primary_box.pack_start(use_primary_checkbutton)

		self.synch_primary_checkbutton = gtk.CheckButton(_("Synchronize clipboards"))
		if get_use_primary() == True:
			self.synch_primary_checkbutton.set_sensitive(True)
		else:
			self.synch_primary_checkbutton.set_sensitive(False)
		if get_synch_primary() == True:
			self.synch_primary_checkbutton.set_active(True)
		else:
			self.synch_primary_checkbutton.set_active(False)
		self.synch_primary_checkbutton.connect("toggled", self.toggle_synch_primary)
		primary_box.pack_end(self.synch_primary_checkbutton)

		shortcuts_frame = gtk.Frame(_("Keyboard shortcuts"))
		main_prefs_box.pack_start(shortcuts_frame)
		shortcuts_table = gtk.Table(2,2)
		shortcuts_table.set_col_spacing(0, 40)
		shortcuts_table.set_border_width(3)
		shortcuts_frame.add(shortcuts_table)

		sel_diag_show_align = gtk.Alignment(xalign=0.0, yalign=0.5)
		sel_diag_show_label = gtk.Label(_("Selection dialog"))
		sel_diag_show_align.add(sel_diag_show_label)
		shortcuts_table.attach(sel_diag_show_align, 0, 1, 0, 1)

		sel_diag_key = gtk.Entry()
		sel_diag_key.connect("activate", self.change_sel_dialog_key)
		sel_diag_key.set_text(get_sel_dialog_key())
		shortcuts_table.attach(sel_diag_key, 1, 2, 0, 1)

		pref_diag_show_align = gtk.Alignment(xalign=0.0, yalign=0.5)
		pref_diag_show_label = gtk.Label(_("Preferences dialog"))
		pref_diag_show_align.add(pref_diag_show_label)
		shortcuts_table.attach(pref_diag_show_align, 0, 1, 1, 2)
		
		pref_diag_key = gtk.Entry()
		pref_diag_key.connect("activate", self.change_pref_dialog_key)
		pref_diag_key.set_text(get_prefs_dialog_key())
		shortcuts_table.attach(pref_diag_key, 1, 2, 1, 2)

		# Interface tab
		interface_prefs_box = gtk.VBox()
		ntbk.append_page(interface_prefs_box, gtk.Label(_("Interface")))

		menu_frame = gtk.Frame(_("Menu"))
		interface_prefs_box.pack_start(menu_frame)

		menu_box = gtk.VBox()
		menu_box.set_border_width(3)
		menu_frame.add(menu_box)

		item_length_pref_box = gtk.HBox()
		item_length_pref_align = gtk.Alignment(xalign=0.0, yalign=0.5)
		item_length_pref_label = gtk.Label(_("Menu history entries length"))
		item_length_pref_align.add(item_length_pref_label)
		item_length_pref_box.pack_start(item_length_pref_align)
	
		self.item_length_pref_spin = gtk.SpinButton(gtk.Adjustment(lower=20.0, upper=60.0, step_incr=1.0))
		self.item_length_pref_spin.set_value(get_item_length())
		self.item_length_pref_spin.connect("value-changed", self.change_item_length)
		item_length_pref_box.pack_end(self.item_length_pref_spin)

		menu_box.pack_start(item_length_pref_box, expand=False)

		special_menuitems_frame = gtk.Frame(_("Special menu items"))
		special_menuitems_box = gtk.VBox()
		special_menuitems_box.set_border_width(3)

		show_prefs_checkbutton = gtk.CheckButton(_("Show 'preferences' on menu"))
		if get_show_prefs() == True:
			show_prefs_checkbutton.set_active(True)
		else:
			show_prefs_checkbutton.set_active(False)
		show_prefs_checkbutton.connect("toggled", self.toggle_show_prefs)
		special_menuitems_box.pack_start(show_prefs_checkbutton, expand=False)

		show_misc_checkbutton = gtk.CheckButton(_("Show 'quit' on menu"))
		if get_show_quit() == True:
			show_misc_checkbutton.set_active(True)
		else:
			show_misc_checkbutton.set_active(False)
		show_misc_checkbutton.connect("toggled", self.toggle_show_quit)
		special_menuitems_box.pack_start(show_misc_checkbutton, expand=False)

		menu_box.pack_end(special_menuitems_frame)
		special_menuitems_frame.add(special_menuitems_box)

		# window preparation
		self.window.show_all()
		self.window.show()
		self.window.connect("key-press-event", self.keyboard_handler)

	def toggle_show_quit(self, event):
		if get_show_quit() == True:
			set_show_quit(0)
		else:
			set_show_quit(1)
	
	def toggle_show_prefs(self, event):
		if get_show_prefs() == True:
			set_show_prefs(0)
		else:
			set_show_prefs(1)

	def toggle_use_primary(self, event):
		if get_use_primary() == True:
			set_use_primary(0)
			self.synch_primary_checkbutton.set_sensitive(False)
		else:
			set_use_primary(1)
			self.synch_primary_checkbutton.set_sensitive(True)

	def toggle_synch_primary(self, event):
		if get_synch_primary() == True:
			set_synch_primary(0)
		else:
			set_synch_primary(1)

	def change_history_size(self, event):
		set_history_size(int(self.hist_size_pref_spin.get_value()))

	def change_item_length(self, event):
		set_item_length(int(self.item_length_pref_spin.get_value()))

	def change_sel_dialog_key(self, entry):
		if entry.get_text() != get_sel_dialog_key():
			set_sel_dialog_key(entry.get_text())

	def change_pref_dialog_key(self, entry):
		if entry.get_text() != get_sel_dialog_key():
			set_prefs_dialog_key(entry.get_text())
	
	def keyboard_handler(self, event, data=None):
		key = gtk.gdk.keyval_name(data.keyval)

		if key == "Escape":
			self.window.destroy()


if __name__ == "__main__":
	import gettext
	gettext.install("pastie", "/usr/share/locale")
	w = PreferencesDialog()
	w.window.connect("destroy", lambda q: gtk.main_quit())
	gtk.main()
