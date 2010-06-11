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

import gobject
import gtk
import gtk.gdk
import os.path
import xml.etree.ElementTree as tree
import hashlib

try:
	import pastie.history as history
except:
	import history
try:
	import pastie.edit_clipboard as edit
except:
	import edit_clipboard as edit

class ClipboardProtector():
	def __init__(self, indicator):
		# get the clipboard gdk atom
		self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)

		self.indicator = indicator
		self.clipboard_text = ""

		# create the history data strucure
		self.history = history.HistoryMenuItemCollector()
		# load history if existent
		self.history.set_payload(self.recover_history())
		# show the menu
		self.update_menu()
		
		# register the timeout that checks the clipboard contents
		gobject.timeout_add(500, self.check)

	# returns a list of history items from a XML file.
	def recover_history(self, input_file="~/.clipboard_history"):
		tmp_list = []
		try:
			history_tree = tree.parse(os.path.expanduser(input_file))
		except IOError:
			return tmp_list
		for item in history_tree.findall("item"):
			history_item = history.HistoryMenuItem(item.text, self)
			tmp_list.append(history_item)
		return tmp_list
	
	# saves the clipboard history to a XML file. called on program termination.
	def save_history(self, output_file="~/.clipboard_history"):
		history_tree_root = tree.Element("clipboard")
		for item in self.history.data:
			history_tree_item = tree.SubElement(history_tree_root, "item")
			history_tree_item.set("id", hashlib.md5(item.payload).hexdigest())
			history_tree_item.text = item.payload
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
		# get clipoard plain text
		clipboard_temp = self.clipboard.wait_for_text()
		if clipboard_temp == None and self.clipboard_text != None:
			targets = self.clipboard.wait_for_targets()
			if not targets:
				self.clipboard.set_text(self.clipboard_text)
		else:
			if clipboard_temp != self.clipboard_text:
				if clipboard_temp != "":
					self.clipboard_text = clipboard_temp
					self.history.add(history.HistoryMenuItem(clipboard_temp, self))
					self.update_menu()
					self.save_history()
		return True # so timeout continues.

	# create and show the menu
	def update_menu(self):
		menu = gtk.Menu()
		if len(self.history) > 0:
			self.history.add_items_to_menu(menu)
			separator = gtk.SeparatorMenuItem()
			menu.append(separator)
		edit_clipboard_menu = gtk.MenuItem(_("Edit clipboard"))
		edit_clipboard_menu.connect("activate", lambda w: edit.ClipboardEditorDialog())
		menu.append(edit_clipboard_menu)
		if len(self.history) > 0:
			clean_menu = gtk.MenuItem(_("Clean history"))
			clean_menu.connect("activate", self.clean_history)
			menu.append(clean_menu)
		menu.show_all()
		# attach this menu to the indicator
		self.indicator.set_menu(menu)
