#/usr/bin/env python

import gtk
import sys

def add_to_history(text):
	clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
	clipboard.set_text(text)
	clipboard.store()

def print_current():
	clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
	text = clipboard.wait_for_text()
	if text != None:
		sys.stdout.write(text)
