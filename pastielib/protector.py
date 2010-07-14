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
import appindicator
import os.path
import xml.etree.ElementTree as tree
from xml.parsers.expat import ExpatError
import base64
import hashlib

import pastielib.history as history
import pastielib.edit_clipboard as edit
import pastielib.preferences as prefs

class ClipboardProtector(object):
	def __init__(self):
		# create indicator
		pastieDir = os.path.join(os.path.expanduser('~'), '.pastie/')
		pastieIcon = os.path.join(os.path.expanduser('~'), '.pastie/pastie.svg')
	
		if os.path.isfile(pastieIcon) == True:
			self.indicator = appindicator.Indicator("pastie", "pastie", appindicator.CATEGORY_APPLICATION_STATUS, pastieDir)
		else:
			self.indicator = appindicator.Indicator("pastie", "gtk-paste", appindicator.CATEGORY_APPLICATION_STATUS)
	
		self.indicator.set_status(appindicator.STATUS_ACTIVE)
		
		# get the clipboard gdk atom
		self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
		# check clipboard changes on owner-change event
		self.clipboard.connect("owner-change", self.check)

		self.clipboard_text = ""
		self.clipboard_image = None

		# create the history data strucure
		self.history = history.HistoryMenuItemCollector()
		# the menu will be updated when the "item-lenght-adjusted" signal in the history object is emitted
		self.history.connect("length-adjusted", self.update_menu)
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
	
		# set the gconf_client
		self.gconf_client = prefs.PrefsGConfClient()
	
		# register gconf preferences changes  callback functions
		self.gconf_client.notify_add('show_quit_on_menu', self.update_menu)
		self.gconf_client.notify_add('item_length', self.update_menu)
		self.gconf_client.notify_add('history_size', self.history.adjust_maxlen)

		# register the timeout that checks the clipboard contents
		gobject.timeout_add(500, self.check_specials)

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
				data = base64.b64decode(item.text)
				has_alpha = bool(item.get("has_alpha"))
				width = int(item.get("width"))
				height = int(item.get("height"))
				rowstride = int(item.get("rowstride"))
				pixbuf = gtk.gdk.pixbuf_new_from_data(data, gtk.gdk.COLORSPACE_RGB, has_alpha, 8, width, height, rowstride)
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
					
			if isinstance(item, history.TextHistoryMenuItem):
				item_type = "text"
			elif isinstance(item, history.FileHistoryMenuItem):
				item_type = "file"
			elif isinstance(item, history.ImageHistoryMenuItem):
				item_type = "image"
			else:
				item_type = "text"
			history_tree_item.set("type", item_type)
			
			if item_type == "image":
				history_tree_item.set("has_alpha", str(item.pixbuf.props.has_alpha))
				history_tree_item.set("width", str(item.pixbuf.props.width))
				history_tree_item.set("height", str(item.pixbuf.props.height))
				history_tree_item.set("rowstride", str(item.pixbuf.props.rowstride))
				history_tree_item.text = base64.b64encode(item.payload)
			else:
				history_tree_item.text = item.payload

		history_tree = tree.ElementTree(history_tree_root)
		history_tree.write(os.path.expanduser(output_file), "UTF-8")

	# erase the clipboard history. the current contents of the clipoard will remain.
	def clean_history(self, event=None):
		self.history.empty()
		self.clipboard_text = ""
		self.clipboard_image = None
		self.check()
		self.update_menu()
	
	# check clipboard contents.
	def check(self, clipboard=None, event=None):
		if not self.clipboard.wait_for_targets():
			if self.clipboard_text != "" or self.clipboard_image != None:
				if self.clipboard_text != "" : self.clipboard.set_text(self.clipboard_text)
				if self.clipboard_image != None: self.clipboard.set_image(self.clipboard_image)
				self.clipboard.store()
		elif self.clipboard.wait_is_text_available():
			clipboard_tmp = self.clipboard.wait_for_text()
			if clipboard_tmp not in ("", None):
				if clipboard_tmp != self.clipboard_text:
					if self.clipboard.wait_is_uris_available():
						self.history.add(history.FileHistoryMenuItem(clipboard_tmp, self))
					else:
						self.history.add(history.TextHistoryMenuItem(clipboard_tmp, self))
					self.clipboard_text = clipboard_tmp
					# update menu
					self.update_menu()
					# save history
					self.save_history()
		elif self.clipboard.wait_is_image_available():
			clipboard_contents = self.clipboard.wait_for_image()
			if self.clipboard_image == None or clipboard_contents.get_pixels() != self.clipboard_image.get_pixels():
				self.history.add(history.ImageHistoryMenuItem(clipboard_contents, self))
				self.clipboard_image = clipboard_contents
				# update menu
				self.update_menu()
				# save history
				self.save_history()
		return True

	def check_specials(self):
		targets = self.clipboard.wait_for_targets()
		if targets != None:
			if '_VIM_TEXT' in targets:
				clipboard_tmp = self.clipboard.wait_for_text()
				if clipboard_tmp not in ("", None) and clipboard_tmp != self.clipboard_text:
					self.history.add(history.TextHistoryMenuItem(clipboard_tmp, self))
					self.clipboard_text = clipboard_tmp
					self.update_menu()
					self.save_history()
		return True
	
	# create and show the menu
	def update_menu(self, gconfclient=None, gconfentry=None, gconfvalue=None, d=None):
		menu = gtk.Menu()
		if len(self.history) > 0:
			self.history.add_items_to_menu(menu)
			menu.append(gtk.SeparatorMenuItem())
		if self.history[0] and isinstance(self.history[0], history.TextHistoryMenuItem):
			edit_clipboard_menu = gtk.MenuItem(_("Edit clipboard"))
			edit_clipboard_menu.connect("activate", lambda w: edit.ClipboardEditorDialog())
			menu.append(edit_clipboard_menu)
		if len(self.history) > 0:
			clean_menu = gtk.MenuItem(_("Clean history"))
			clean_menu.connect("activate", self.clean_history)
			menu.append(clean_menu)
		if prefs.get_show_quit() == True:
			quit_menu = gtk.MenuItem(_("Quit"))
			quit_menu.connect("activate", lambda q: gtk.main_quit())
			menu.append(quit_menu)
		menu.show_all()
		# attach this menu to the indicator
		self.indicator.set_menu(menu)
