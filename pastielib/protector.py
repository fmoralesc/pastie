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

import gobject
import gtk
import gtk.gdk
import os.path
import xml.etree.ElementTree as tree
from xml.parsers.expat import ExpatError
import hashlib

import pastielib.history as history
import pastielib.edit_clipboard as edit
import pastielib.preferences as prefs

class ClipboardProtector(object):
	def __init__(self, indicator):
		# set the gconf_client
		self.gconf_client = prefs.PrefsGConfClient()
		
		# get the clipboard gdk atom
		self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)

		self.indicator = indicator
		self.clipboard_text = ""

		# create the history data strucure
		self.history = history.HistoryMenuItemCollector(self)
		# load history if existent
		self.history.set_payload(self.recover_history())
		# pastie might have been loaded after some contents were added to the X clipboard.
		# we check if ther's any.
		self.check()
		# select the first item in the history.
		if len(self.history) > 0:
			self.history[0].set_as_current()

		# show the menu
		self.update_menu()
		
		# register gconf preferences changes  callback functions
		self.gconf_client.notify_add('show_quit_on_menu', self.update_menu)
		self.gconf_client.notify_add('item_length', self.update_menu)
		self.gconf_client.notify_add('history_size', self.history.adjust_maxlen)

		# register the timeout that checks the clipboard contents
		gobject.timeout_add(500, self.check)

	# returns a list of history items from a XML file.
	def recover_history(self, input_file="~/.clipboard_history"):
		tmp_list = []
		try:
			history_tree = tree.parse(os.path.expanduser(input_file))
		except IOError: # file doesn't exist
			return tmp_list
		except ExpatError: # file is empty or malformed
			return tmp_list
		for item in history_tree.findall("item"):
			if item.get("type") == "text":
				history_item = history.TextHistoryMenuItem(item.text, self)
			elif item.get("type") == "file":
				history_item = history.FileHistoryMenuItem(item.text, self)
			elif item.get("type") == "image":
				data = item.text
				has_alpha = bool(item.get("has_alpha"))
				width = int(item.get("width"))
				height = int(item.get("height"))
				rowstride = int(item.get("rowstride"))
				pixbuf = gtk.pixbuf_new_from_data(data, gtk.gdk.COLORSPACE_RGB, has_alpha, 8, width, height, rowstride)
				history_item = history.ImageHistoryMenuItem(pixbuf, self)
			else:
				history_item = history.TextHistoryMenuItem(item.text, self)
			tmp_list.append(history_item)
		return tmp_list
	
	# saves the clipboard history to a XML file. called on program termination.
	def save_history(self, output_file="~/.clipboard_history"):
		history_tree_root = tree.Element("clipboard")
		for item in self.history.data:
			history_tree_item = tree.SubElement(history_tree_root, "item")
			history_tree_item.set("id", hashlib.md5(item.payload).hexdigest())
			
			if isinstance(history_tree_item, history.TextHistoryMenuItem):
				item_type = "text"
			elif isinstance(history_tree_item, history.FileHistoryMenuItem):
				item_type = "file"
			elif isinstance(history_tree_item, history.ImageHistoryMenuItem):
				item_type = "image"
			else:
				item_type = "text"
			history_tree_item.set("type", item_type)

			if item_type in ("text", "file"):
				history_tree_item.text = item.payload
			elif item_type == "image":
				history_tree_item.set("has_alpha", str(item.payload.props.has_alpha))
				history_tree.item.set("width", str(item.payload.props.width))
				history_tree_item.set("height", str(item.payload.props.height))
				history_tree_item.set("rowstride", str(item.payload.props.rowstride))
				history_tree_item.text = item.payload.get_pixels()

		history_tree = tree.ElementTree(history_tree_root)
		history_tree.write(os.path.expanduser(output_file), "UTF-8")

	# erase the clipboard history. the current contents of the clipoard will remain.
	def clean_history(self, event=None):
		self.history.empty()
		self.clipboard_text = ""
		self.update_menu()
	
	# check clipboard contents.
	# the procedure was taken from parcellite code.
	def check(self):
		clipboard_text_available = self.clipboard.wait_is_text_available()
		if not clipboard_text_available and self.clipboard_text != None:
			targets = self.clipboard.wait_for_targets()
			if not targets:
				self.clipboard.set_text(self.clipboard_text)
				self.clipboard.store()
		else:
			clipboard_temp = self.clipboard.wait_for_text()
			if clipboard_temp != self.clipboard_text:
				if clipboard_temp != "":
					self.clipboard_text = clipboard_temp
					self.history.add(history.TextHistoryMenuItem(clipboard_temp, self))
					self.update_menu()
					self.save_history()
		return True # so timeout continues.

	# create and show the menu
	def update_menu(self, gconfclient=None, gconfentry=None, gconfvalue=None, d=None):
		menu = gtk.Menu()
		if len(self.history) > 0:
			self.history.add_items_to_menu(menu)
			menu.append(gtk.SeparatorMenuItem())
		edit_clipboard_menu = gtk.MenuItem(_("Edit clipboard"))
		edit_clipboard_menu.connect("activate", lambda w: edit.ClipboardEditorDialog())
		menu.append(edit_clipboard_menu)
		if len(self.history) > 0:
			clean_menu = gtk.MenuItem(_("Clean history"))
			clean_menu.connect("activate", self.clean_history)
			menu.append(clean_menu)
		if self.gconf_client.get_show_quit() == True:
			quit_menu = gtk.MenuItem(_("Quit"))
			quit_menu.connect("activate", lambda q: gtk.main_quit())
			menu.append(quit_menu)
		menu.show_all()
		# attach this menu to the indicator
		self.indicator.set_menu(menu)
