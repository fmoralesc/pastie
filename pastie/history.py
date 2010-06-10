#!/usr/bin/env python
# coding=utf8

import gtk
import gtk.gdk
import textwrap

class HistoryMenuItem():
	def __init__(self, item, protector):
		self.payload = item
		self.protector = protector
		self.collector = protector.history
		self.normal = self.repr(self.payload)
		self.selected = self.decorate(self.repr(self.payload))
	
	def repr(self, content, length=50):
		try:
			if len(content) <= length:
				return content.strip()
			else:
				return textwrap.wrap(content, length - 3)[0] + "..."
		except:
			return ""

	def decorate(self, content):
		try:
			return "<b>" + content + "</b>"
		except:
			return content

	def set_as_current(self, event):
		self.collector.select(self)
		self.protector.update_menu()
		self.protector.clipboard.set_text(self.payload)

class HistoryCollector():
	def __init__(self, maxlen=25):
		self.iter_count = -1
		self.maxlen = maxlen
		self.data = []

	def set_payload(self, payload):
		self.data = payload

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

	def repr(self):
		count = 0
		for i in self:
			if count == 0:
				try:
					print i.selected
				except:
					print i
			else:
				try:
					print i.normal
				except:
					print i
			count =+ 1

	def exists(self,data):
		for item in self:
			if item.payload == data.payload:
				return True
		return False

	def existing_index(self, data):
		count = 0
		for item in self:
			if item.payload == data.payload:
				return count
			count =+ 1
		return -1

	def add(self,data):
		# si no existe ya en el historial
		if not self.exists(data):
			# si no tenemos contenidos ...
			if len(self.data) == 0:
				# simplemente añadimos los datos
				self.data.append(data)
			# si ya tenemos contenidos ...
			else:
				# cogemos los datos que queremos preservar
				tail = self.data[0:self.maxlen - 1]
				# limpiamos la lista
				self.data = []
				# añadimos los datos nuevos
				self.data.append(data)
				# añadimos los datos que queríamos preservar
				for item in tail:
					self.data.append(item)
		# si ya existen los datos, los seleccionamos
		else:
			found_at = self.existing_index(data)
			if found_at != -1:
				self.select(self.data[found_at])

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

	def empty(self):
		self.data = []

class HistoryMenuItemCollector(HistoryCollector):
	def add_items_to_menu(self, menu):
		count = 0
		for i in self:
			if count == 0:
				item = gtk.MenuItem(i.selected)
				item.get_child().set_use_markup(True)
			else:
				item = gtk.MenuItem(i.normal)
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
