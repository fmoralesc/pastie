#!/usr/bin/env python

#    pastie - a simple clipboard manager
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
import gtk.gdk

class ClipboardEditorDialog():
	def __init__(self):
		self.clipboard = gtk.clipboard_get()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(_("Editing clipboard"))
		self.window.set_resizable(False)
		self.window.set_skip_pager_hint(True)
		self.window.set_skip_taskbar_hint(True)

		table = gtk.Table(10, 9, True)
		table.set_row_spacings(1)
		self.window.add(table)
		
		textscroll = gtk.ScrolledWindow()
		textscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.textview = gtk.TextView()
		self.textview.set_editable(True)
		self.textview.set_wrap_mode(gtk.WRAP_WORD)
		self.textview.get_buffer().set_text(self.clipboard.wait_for_text())
		textscroll.add(self.textview)

		table.attach(textscroll, 0, 9, 0, 9)

		cancel_button = gtk.Button(_("Cancel"))
		ok_button = gtk.Button(_("Accept"))
		cancel_button.connect("clicked", self.cancel_action)
		ok_button.connect("clicked", self.ok_action)

		table.attach(cancel_button, 7, 8, 9, 10)
		table.attach(ok_button, 8, 9, 9, 10)
		
		self.window.show_all()
		self.window.show()
	
	def cancel_action(self, event):
		self.window.destroy()
	
	def ok_action(self, event):
		textbuffer = self.textview.get_buffer()
		gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD).set_text(textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter()))
		self.window.destroy()

if __name__ == "__main__":
	w = ClipboardEditorDialog()
	gtk.main()
