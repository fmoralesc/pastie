#!/usr/bin/env python

from distutils.core import setup

setup(
	name = "pastie",
	decription = "a simple clipboard manager", 
	author = "Felipe Morales",
	author_email = "hel.sheep@gmail.com",
	url = "http://github.com/fmoralesc/pastie/",
	license = "GNU GPL v3",
	version = "0.3.3",
	scripts = ["pastie"],
	data_files=[
		('/usr/share/applications', ['pastie.desktop']),
		('/usr/share/locale/es/LC_MESSAGES', ['po/es/pastie.mo'])
		],
	packages = ["pastielib"])
