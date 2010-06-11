#!/usr/bin/env python

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

import gettext
import gtk
import appindicator

import pastie.protector as protector

if __name__ == "__main__":
	# load translations
	gettext.install("pastie", "/usr/share/locale")
	
	# create indicator
	indicator = appindicator.Indicator("pastie", "gtk-paste", appindicator.CATEGORY_APPLICATION_STATUS)
	indicator.set_status(appindicator.STATUS_ACTIVE)

	# create clipboard protector (this is the core of the program)
	clipboard_protector = protector.ClipboardProtector(indicator)

	gtk.main()
