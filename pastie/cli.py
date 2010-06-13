#/usr/bin/env python

#    This file is part of pastie - a simple clipboard manager
#    Copyright (C) 2010  Felipe Morales <hel.sheep@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
