import gobject
import gtk

class SelectionDialog():
	def __init__(self, protector):
		self.index = 0

		self.protector = protector
		
		self.window = gtk.Window()
		self.window.set_modal(True)
		self.window.set_border_width(1)
		self.window.set_skip_pager_hint(True)
		self.window.set_skip_taskbar_hint(True)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_decorated(False)
		self.window.set_keep_above(True)
		self.window.set_resizable(False)

		self.textview = gtk.TextView()
		self.textview.set_size_request(240,64)
		self.textview.set_editable(False)
		self.textview.set_cursor_visible(False)
		self.textview.set_wrap_mode(gtk.WRAP_WORD)

		self.arrows = gtk.HBox()
		self.arrow_left = gtk.Label()
		self.arrow_left.set_use_markup(True)
		self.arrow_right = gtk.Label()
		self.arrow_right.set_use_markup(True)
		self.arrows.add(self.arrow_left)
		self.arrows.add(self.arrow_right)
		self.arrows.show_all()
		self.textview.add_child_in_window(self.arrows, gtk.TEXT_WINDOW_TEXT, 215, 45)

		self.search = gtk.Entry()
		self.search.set_has_frame(False)
		self.search.show()
		self.textview.add_child_in_window(self.search, gtk.TEXT_WINDOW_TEXT, 0, 45)
		
		self.window.add(self.textview)
		self.textview.show()

		self.window.set_focus_chain((self.search,))
	
		self.window.connect("key-press-event", self.handle_keypresses)
	
	def show(self):
		gobject.timeout_add(100, self.present)

	def present(self):
		self.textview.get_buffer().set_text(self.protector.history[self.index].get_long_label())
		self.search.grab_focus()
		self.search.set_text("")
		self.next_result = 0
		self.window.stick()
		self.window.present()
		self.update_labels()

	def hide(self):
		self.index = 0
		self.window.hide()

	def update_labels(self):
		self.arrow_left.set_markup('<span size="9000" background="grey" foreground="white">'+u"\u21e7"+'</span>')
		self.arrow_right.set_markup('<span size="9000" background="grey" foreground="white">'+u"\u21e9"+'</span>')
		if self.index == 0:
			self.arrow_left.set_markup('<span size="9000">'+u"\u21e7"+"</span>")
		if self.index == len(self.protector.history) - 1:
			self.arrow_right.set_markup('<span size="9000">'+u"\u21e9"+"</span>")

	def handle_keypresses(self, widget, data=None):
		key = gtk.gdk.keyval_name(data.keyval)

		if key == "Escape":
			self.hide()
		
		elif key in ("Up", "Down", "Left", "Right"): #move around the history
			if key in ("Down", "Left"):
				if self.index < (len(self.protector.history)-1):
					self.index = self.index + 1
			elif key in ("Up", "Right"):
				if self.index > 0:
					self.index = self.index - 1
			self.textview.get_buffer().set_text(self.protector.history[self.index].get_long_label())
			self.update_labels()
		
		elif key == "Return": # select current view as the clipboard contents
			self.protector.history.select(None, self.protector.history[self.index])
			self.protector.history[0].set_as_current()
			self.hide()
		
		elif key == "Alt_L": # search
			
			search_text = self.search.get_text()
			try:
				if self.old_search_text != search_text:
					self.next_result = 0
			except:
				pass
			search_results = self.protector.history.find(search_text)
			if search_results == []:
				self.search.set_text(_("Not found!"))
			else:
				self.index = search_results[self.next_result]
				textbuffer = self.textview.get_buffer()
				hightlight = textbuffer.create_tag(background="#ffff00")
				text = self.protector.history[self.index].get_long_label(search_text)
				textbuffer.set_text(text)
				start = text.find(search_text)
				end = start + len(search_text)
				if start > -1:
					iter_start = textbuffer.get_iter_at_offset(start)
					iter_end = textbuffer.get_iter_at_offset(end)
					textbuffer.apply_tag(hightlight,iter_start, iter_end)
				self.update_labels()
				if self.next_result + 1 < len(search_results):
					self.next_result = self.next_result + 1
				else:
					self.next_result = 0
			self.old_search_text = search_text

		
		elif key in ("BackSpace", "Delete"): # clear searches without results
			if self.search.get_text() == _("Not found!"):
				self.search.set_text("")
