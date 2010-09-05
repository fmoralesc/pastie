import gobject
import gtk

class SelectionDialog():
	def __init__(self, protector):
		self.index = 0

		self.protector = protector
		
		self.window = gtk.Window()
		self.window.set_modal(True)
		self.window.set_border_width(6)
		self.window.set_skip_pager_hint(True)
		self.window.set_skip_taskbar_hint(True)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.set_decorated(False)
		self.window.set_keep_above(True)
		self.window.set_resizable(False)

		self.textview = gtk.TextView()
		self.textview.set_size_request(240,60)
		self.textview.set_editable(False)
		self.textview.set_cursor_visible(False)
		self.textview.set_wrap_mode(gtk.WRAP_WORD)

		self.arrows = gtk.Label("hey!")
		self.arrows.show()
		self.textview.add_child_in_window(self.arrows, gtk.TEXT_WINDOW_TEXT, 212, 40)

		self.window.add(self.textview)
		self.textview.show()
	
		self.window.connect("key-press-event", self.handle_keypresses)
	
	def show(self):
		gobject.timeout_add(100, self.present)

	def present(self):
		self.textview.get_buffer().set_text(self.protector.history[self.index].get_long_label())
		self.window.stick()
		self.window.present()

	def handle_keypresses(self, widget, data=None):
		key = gtk.gdk.keyval_name(data.keyval)
		if key == "Escape":
			self.index = 0
			self.window.hide()
		elif key in ("Up", "Down", "Left", "Right"):
			if key in ("Down", "Left"):
				if self.index < (len(self.protector.history)-1):
					self.index = self.index + 1
			elif key in ("Up", "Right"):
				if self.index > 0:
					self.index = self.index - 1
			self.textview.get_buffer().set_text(self.protector.history[self.index].get_long_label())
		elif key == "Return":
			self.protector.history.select(None, self.protector.history[self.index])
			self.protector.history[0].set_as_current()
			self.index = 0
			self.window.hide()
			
