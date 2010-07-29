#!/usr/bin/env python

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
import gtk.gdk

class ClipboardEditorDialog(object):
	def __init__(self, protector):
		self.protector = protector
		self.clipboard = gtk.clipboard_get()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title(_("Editing clipboard"))
		self.window.set_resizable(True)
		self.window.set_skip_pager_hint(True)
		self.window.set_skip_taskbar_hint(True)
		self.window.set_size_request(500, 300)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_border_width(6)

		vbox = gtk.VBox(spacing=6)
		self.window.add(vbox)
		
		textscroll = gtk.ScrolledWindow()
		textscroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.textview = gtk.TextView()
		self.textview.set_editable(True)
		self.textview.set_wrap_mode(gtk.WRAP_WORD)
		self.textview.get_buffer().set_text(self.clipboard.wait_for_text())
		textscroll.add(self.textview)

		vbox.pack_start(textscroll)

		def create_button(stock, clicked):
			button = gtk.Button(stock=stock)
			button.connect("clicked", clicked)
			return button

		hbox = gtk.HButtonBox()
		hbox.set_spacing(6)
		hbox.set_layout(gtk.BUTTONBOX_END)
		
		gtk.stock_add( (('pastie-replace', _("_Replace"), gtk.gdk.MOD1_MASK, gtk.gdk.keyval_from_name(_('R')), 'pastie'),) )
		
		hbox.add(create_button(gtk.STOCK_CANCEL, self.cancel_action))
		hbox.add(create_button(gtk.STOCK_DELETE, self.delete_action))
		hbox.add(create_button("pastie-replace", self.replace_action))
		hbox.add(create_button(gtk.STOCK_OK, self.ok_action))
		
		vbox.pack_end(hbox, expand=False)
		
		self.window.show_all()
		self.window.show()
	
	def cancel_action(self, event):
		self.window.destroy()
	
	def ok_action(self, event):
		textbuffer = self.textview.get_buffer()
		new_text = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter())
		if new_text not in ("", None):
			gtk.clipboard_get().set_text(new_text)
		self.window.destroy()
	
	def delete_action(self, event):
		self.protector.delete_current()
		self.window.destroy()

	def replace_action(self, event):
		textbuffer = self.textview.get_buffer()
		new_text = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter())
		if new_text not in ("", None):
			self.protector.replace_current(new_text)
		self.window.destroy()
		
