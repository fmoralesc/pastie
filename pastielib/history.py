#!/usr/bin/env python
# coding=utf8

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

# class representing history items.
class HistoryMenuItem():
	def __init__(self, item, protector):
		self.payload = item
		self.protector = protector
		self.collector = protector.history
		
	def repr(self, length=50):
		l = unicode(self.payload).strip(' ')
		if len(l) > length:
			l = l[:length-1] + u'\u2026'

		l = l.replace('\t', u'\u22c5')
		l = l.replace('\n', u'\u21b2')
		
		return l

	# set payload as current clipboard content.
	def set_as_current(self, event=None):
		self.collector.select(self)
		self.protector.update_menu()
		self.protector.clipboard.set_text(self.payload)
		self.protector.clipboard.store()

# class representin the history items collection.
class HistoryCollector():
	def __init__(self, maxlen=25): #change maxlen to tweak history size
		self.iter_count = -1
		self.maxlen = maxlen
		self.data = []

	# load data. used when reading history from file.
	def set_payload(self, payload):
		self.data = payload

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
		return self.data[index]

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
				self.data = []
				# add the new data
				self.data.append(data)
				# reappend the data we preserved before
				for item in tail:
					self.data.append(item)
		# if it does exist in collection
		else:
			found_at = self.existing_index(data)
			if found_at != -1:
				# we just select it
				self.select(self.data[found_at])

	# set some item as the current member of the selection (top)
	def select(self, data):
		idx = self.data.index(data)
		selected_data = self.data[idx]
		head = self.data[0:idx]
		tail = self.data[idx + 1:]
		
		self.data = []
		self.data.append(selected_data)
		for item in head:
			self.data.append(item)
		for item in tail:
			self.data.append(item)
	
	# clear the history
	def empty(self):
		self.data = []

# wrapper that adds menuitems to a menu
class HistoryMenuItemCollector(HistoryCollector):
	def add_items_to_menu(self, menu):
		count = 0
		for i in self:
			item = gtk.MenuItem(i.repr())
			item.connect("activate", i.set_as_current)
			menu.append(item)
			count =+ 1

if __name__ == "__main__":
	b = HistoryCollector(maxlen=2)
	c = HistoryMenuItem("help1", b)
	b.add(c)
	d = HistoryMenuItem("help2", b)
	b.add(d)
	b.repr()
	c.set_as_current(None)
	b.repr()
	e = HistoryMenuItem("help3", b)
	b.add(e)
	b.repr()
