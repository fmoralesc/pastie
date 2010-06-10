#!/usr/bin/env python

import signal
import atexit
import gettext
import gtk
import appindicator

import pastie.protector as protector

if __name__ == "__main__":
	gettext.install("pastie", "/usr/share/locale")
	indicator = appindicator.Indicator("pastie", "gtk-paste", appindicator.CATEGORY_APPLICATION_STATUS)
	indicator.set_status(appindicator.STATUS_ACTIVE)

	clipboard_protector = protector.ClipboardProtector(indicator)

	signal.signal(signal.SIGTERM, clipboard_protector.save_history)
	atexit.register(clipboard_protector.save_history)
	gtk.main()
