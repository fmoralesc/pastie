#!/usr/bin/env python

from distutils.core import setup

setup(
	name = "pastie",
	description = "a simple clipboard manager", 
	author = "Felipe Morales",
	author_email = "hel.sheep@gmail.com",
	url = "http://github.com/fmoralesc/pastie/",
	license = "GNU GPL v3",
	version = "0.4",
	scripts = ["pastie"],
	data_files=[
		('/usr/share/applications', ['pastie.desktop']),
		('/etc/xdg/autostart', ['pastie-startup.desktop']),
		('/usr/share/gconf/schemas', ['pastie.schemas']),
		('/usr/share/locale/es/LC_MESSAGES', ['po/es/pastie.mo']),
		('/usr/share/locales/ja/LC_MESSAGES', ['po/ja/pastie.mo']),
		('/usr/share/locale/ru/LC_MESSAGES', ['po/ru/pastie.mo']),
		('/usr/share/locale/uk/LC_MESSAGES', ['po/uk/pastie.mo']),
		],
	packages = ["pastielib"])
