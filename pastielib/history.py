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
import os.path
from fractions import Fraction

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
		l = l.replace('_', '__')
		
		return l

	def set_as_current(self, event=None):
		HistoryMenuItem.set_as_current(self, event)
		gtk.clipboard_get().set_text(self.payload)
		gtk.clipboard_get().store()

# class representing file items
class FileHistoryMenuItem(HistoryMenuItem):
	def get_label(self):
		# this shortens a pair of strings proportionally given a size constraint.
		def balanced_constraint_shorten(pair, constraint):
			total_length_to_shorten = len(pair[0]) + len(pair[1])

			if constraint < total_length_to_shorten:
				size_to_reduce = abs(constraint - total_length_to_shorten)
				
				string_ratio = Fraction(len(pair[0]),len(pair[1]))
				first_ratio, second_ratio = string_ratio.numerator, string_ratio.denominator
				total = string_ratio.denominator + string_ratio.numerator
				
				size_of_first_cut = (first_ratio * size_to_reduce / total) + 1
				first_remainder_size = len(pair[0]) - size_of_first_cut
				size_of_second_cut = (second_ratio * size_to_reduce / total) + 1
				second_remainder_size = len(pair[1]) - size_of_second_cut

				first_extreme_size = first_remainder_size/2
				if first_extreme_size == 0:
					first_extreme_size = 1
				second_extreme_size = second_remainder_size/2
				if second_extreme_size == 0:
					second_extreme_size = 1

				first = pair[0][:first_extreme_size] + u"\u2026" + pair[0][first_extreme_size+size_of_first_cut:]
				if len(first) == len(pair[0]):
					first = pair[0]
				second = pair[1][:second_extreme_size] + u"\u2026" + pair[1][second_extreme_size+size_of_second_cut:]
				if len(second) == len(pair[1]):
					second = pair[1]
				
				# we might have missed it by 1
				preliminary_lenght = len(first) + len(second)
				if preliminary_lenght > constraint:
					if len(first) > len(second):
						first = pair[0][:first_extreme_size] + u"\u2026" + pair[0][first_extreme_size+size_of_first_cut+1:]
					elif len(second) > len(first):
						second = pair[1][:second_extreme_size] + u"\u2026" + pair[1][second_extreme_size+size_of_second_cut+1:]

				return first, second
			else:
				return pair

		lines = self.payload.split("\n")
		
		# we want to see if there are more files than the one shown
		if len(lines) > 1:
			label = "  (+ " + str(len(lines)-1) + " " + _("more") + ") "
		else:
			label = ""
		
		# we'll want to see if it's a regular file or a dir
		if os.path.isdir(lines[0]):
			first_file_tail = "/"
		else:
			first_file_tail = ""
		first_file = os.path.basename(lines[0]) + first_file_tail

		# common_path is the folder where the copied files reside
		if len(lines) == 1:
			if os.path.dirname(lines[0]) == "/":
				common_path = "/"
			else:
				common_path = os.path.dirname(lines[0]) + "/"
		else:
			common_path = os.path.dirname(os.path.commonprefix(lines)) + "/"
		common_path = common_path.replace(os.path.expanduser("~"), "~")
		path_list = common_path.split("/")
		last = len(path_list)-2
		for d in range(last):
			try:
				path_list[d] = path_list[d][0]
			except IndexError:
				pass
		# we shorten the label, if it's needed
		available = prefs.get_item_length() - len(label) - len("/".join(path_list[:last-1])) - 5
		first_file, path_list[last] = balanced_constraint_shorten((first_file, path_list[last]), available)

		common_path = "/".join(path_list)

		name_part = first_file + label
		path_part = " [ " + common_path + " ]"
		
		l = u"\u25A4 " + name_part + path_part
		l = l.replace("_", "__")
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
		l = u"\u25A3 [" + str(self.pixbuf.props.width) + u"\u2715" + str(self.pixbuf.props.height) + "]"
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
				self.emit("data-change", len(self))
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

	def delete_top(self):
		self.data = self.data[1:]
		if len(self) > 0:
			self.select(None, self.data[0])
		self.emit("data-change", len(self))
	
	def replace_top(self, data):
		self.data[0] = data
		self.select(None, self.data[0])
		self.emit("data-change", len(self))

	def adjust_maxlen(self, gconf=None, key=None, value=None, d=None):
		self.maxlen = prefs.get_history_size()
		for i in self.data[self.maxlen:]:
			del i
		self.data = self.data[:self.maxlen]
		self.emit("length-adjusted", self.maxlen)

def new_signal(label, class_name, flag=gobject.SIGNAL_ACTION, ret=None, args=(int,)):
	gobject.signal_new(label, class_name, flag, ret, args)

new_signal("data-change", HistoryMenuItemCollector)
new_signal("length-adjusted", HistoryMenuItemCollector)
new_signal("select", HistoryMenuItem, args=(object,))
