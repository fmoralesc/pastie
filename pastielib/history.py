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
import gnomevfs

import pastielib.preferences as prefs

# parent class for history menu items
class HistoryMenuItem(gobject.GObject):
	def __init__(self, item):
		gobject.GObject.__init__(self)
		self.payload = item

	# subclasses must override this
	def get_label(self):
		pass

	# set payload as current clipboard content.
	# subclasses must extend this.
	def set_as_current(self, event=None):
		self.emit("select", self)

# class representing text items.
class TextHistoryMenuItem(HistoryMenuItem):
	def get_label(self):
		length = prefs.get_item_length()
		l = unicode(self.payload[:length+length]).strip(' ')
		if len(l) > length:
			l = l[:length-1] + u'\u2026'

		l = l.replace('\t', u'\u22c5')
		l = l.replace('\n', u'\u21b2')
		
		return l

	def set_as_current(self, event=None):
		HistoryMenuItem.set_as_current(self, event)
		gtk.clipboard_get().set_text(self.payload)
		gtk.clipboard_get().store()

# class representing file items
class FileHistoryMenuItem(HistoryMenuItem):
	def get_label(self):
		length = prefs.get_item_length()
		lines = self.payload.split("\n")
		files_with_comma = unicode(",".join(lines)[:length+length])
		if len(files_with_comma) > length:
			files_with_comma = files_with_comma[:length-1] + u'\u2026'
		if len(lines) == 1:
			l = "[file: " + files_with_comma + "]"
		else:
			l = "[" + str(len(lines)) + " files: " + files_with_comma + "]"
		return l

	def set_as_current(self, event=None):
		def path_get(clipboard, selectiondata, info, path):
			selectiondata.set_text(path)
			files = path.split("\n")
			file_paths = []
			for copied_file in files:
				file_path = gnomevfs.escape_path_string(copied_file)
				file_paths.append('file://' + file_path)
			selectiondata.set_uris(file_paths)
			selectiondata.set('x-special/gnome-copied-files', 8, 'copy\n' + '\n'.join(file_paths))

		def path_clear(self, path):
			return

		HistoryMenuItem.set_as_current(self, event)
		targets = gtk.target_list_add_uri_targets()
		targets = gtk.target_list_add_text_targets(targets)
		targets.append(('x-special/gnome-copied-files', 0, 0))

		gtk.clipboard_get().set_with_data(targets, path_get, path_clear, self.payload)
		gtk.clipboard_get().store()

# class representing image items
class ImageHistoryMenuItem(HistoryMenuItem):
	def __init__(self, item):
		gobject.GObject.__init__(self)
		self.pixbuf = item
		self.payload = self.pixbuf.get_pixels()
	
	def get_label(self):
		l = "[image: " + str(self.pixbuf.props.width) + u"\u2715" + str(self.pixbuf.props.height) + "]"
		return l

	def set_as_current(self, event=None):
		HistoryMenuItem.set_as_current(self, event)
		gtk.clipboard_get().set_image(self.pixbuf)
		gtk.clipboard_get().store()

# class representin the history items collection.
class HistoryMenuItemCollector(gobject.GObject):
	def __init__(self): #change maxlen to tweak history size
		gobject.GObject.__init__(self)
		self.iter_count = -1
		self.data = []
		self.maxlen = prefs.get_history_size()

	# load data. used when reading history from file.
	def set_payload(self, payload):
		for item in payload:
			if len(self.data) < self.maxlen:
				self.data.append(item)
		for item in self:
			item.connect("select", self.select)
		self.emit("data-change", len(self))

	# returns the number of members of collection
	def __len__(self):
		count = 0
		for i in self:
			count =+ 1
		return count
	
	def __iter__(self):
		return self

	def next(self):
		self.iter_count += 1
		if self.iter_count == len(self.data):
			self.iter_count = -1
			raise StopIteration
		else:
			return self.data[self.iter_count]

	def __getitem__(self, index):
		try:
			return self.data[index]
		except:
			return None
		
	# print a representation of the data. for debug purposes only.
	def repr(self):
		count = 0
		for i in self:
			print i
			count =+ 1

	# check if item exists in collection by content comparison.
	def exists(self,data):
		for item in self:
			if item.payload == data.payload:
				return True
		return False
	
	# returns position of existing item.
	def existing_index(self, data):
		count = 0
		for item in self:
			if item.payload == data.payload:
				return count
			count =+ 1
		return -1

	# adds a member to the collection
	def add(self,data):
		# if it doesn't exist in the collection
		if not self.exists(data):
			# if we have no history
			if len(self.data) == 0:
				# we simply add the new data
				self.data.append(data)
			# if we have history data
			else:
				# we grab the data we want to preserve
				tail = self.data[0:self.maxlen - 1]
				# clean the collection
				for i in self.data:
					del i
				self.data = []
				# add the new data
				self.data.append(data)
				# reappend the data we preserved before
				for item in tail:
					self.data.append(item)
				self.emit("data-change", len(self))
			for item in self:
				item.connect("select", self.select)
		# if it does exist in collection
		else:
			found_at = self.existing_index(data)
			if found_at != -1:
				# we just select it
				self.select(self.data[found_at])

	# set some item as the current member of the selection (top)
	def select(self, event, data):
		idx = self.data.index(data)
		selected_data = self.data[idx]
		head = self.data[0:idx]
		tail = self.data[idx + 1:]
		
		for i in self.data:
			del i
		self.data = []
		self.data.append(selected_data)
		for item in head:
			self.data.append(item)
		for item in tail:
			self.data.append(item)
		self.emit("data-change", len(self))
	
	# clear the history
	def empty(self, full=True):
		if full == True:
			for i in self.data:
				del i
			self.data = []
		else:
			for i in self.data[1:]:
				del i
			self.data = [self.data[0]]
		self.emit("data-change", len(self))

	def adjust_maxlen(self, gconf=None, key=None, value=None, d=None):
		self.maxlen = prefs.get_history_size()
		for i in self.data[self.maxlen:]:
			del i
		self.data = self.data[:self.maxlen]
		self.emit("length-adjusted", self.maxlen)

	def add_items_to_menu(self, menu):
		for i in self:
			label = i.get_label()
			item = gtk.MenuItem(label)
			item.connect("activate", i.set_as_current)
			menu.append(item)

def new_signal(label, class_name, flag=gobject.SIGNAL_ACTION, ret=None, args=(int,)):
	gobject.signal_new(label, class_name, flag, ret, args)

new_signal("data-change", HistoryMenuItemCollector)
new_signal("length-adjusted", HistoryMenuItemCollector)
new_signal("select", HistoryMenuItem, args=(object,))
