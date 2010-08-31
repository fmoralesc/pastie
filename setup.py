#!/usr/bin/env python

import os
import os.path
import commands

from distutils.core import setup
from distutils.core import Command
from distutils.command.install import install
from distutils.command.install_data import install_data

setup(
	name = "pastie",
	description = "a simple clipboard manager",
	author = "Felipe Morales",
	author_email = "hel.sheep@gmail.com",
	url = "http://github.com/fmoralesc/pastie/",
	license = "GNU GPL v3",
	version = "0.5.5",
	scripts = ["pastie"],
	data_files=[
		('/usr/share/applications', ['pastie.desktop']),
		('/etc/xdg/autostart', ['pastie-startup.desktop']),
		('/usr/share/gconf/schemas', ['pastie.schemas']),
		('/usr/share/locale/cs/LC_MESSAGES', ['po/cs/pastie.mo']),
		('/usr/share/locale/de/LC_MESSAGES', ['po/de/pastie.mo']),
		('/usr/share/locale/es/LC_MESSAGES', ['po/es/pastie.mo']),
		('/usr/share/locale/ja/LC_MESSAGES', ['po/ja/pastie.mo']),
		('/usr/share/locale/ru/LC_MESSAGES', ['po/ru/pastie.mo']),
		('/usr/share/locale/uk/LC_MESSAGES', ['po/uk/pastie.mo']),
		('/usr/share/locale/it/LC_MESSAGES', ['po/it/pastie.mo']),
		('/usr/share/locale/fi/LC_MESSAGES', ['po/fi/pastie.mo']),
		('/usr/share/locale/he/LC_MESSAGES', ['po/he/pastie.mo']),
		],
	packages = ["pastielib"],)
