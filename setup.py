#!/usr/bin/env python

import os
import os.path
import commands

from distutils.core import setup
from distutils.core import Command
from distutils.command.install import install
from distutils.command.install_data import install_data

class pastie_install(install):
	def initialize_options(self):
		install.initialize_options(self)
	
	def finalize_options(self):
		install.finalize_options(self)

	def check_gconf(self):
		return True

	sub_commands = []
	sub_commands.extend(install.sub_commands)
	sub_commands.append(('install_gconf', check_gconf))

class install_gconf(install_data):
	description = 'install gconf files'

	def initialize_options(self):
		self.gconf_schemas_dir = '/usr/share/gconf/schemas'
		self.gconf_schemas = ['pastie.schemas']
		install_data.initialize_options(self)
	
	def finalize_options(self):
		install_data.finalize_options(self)

	def run(self):
		self.mkpath(self.gconf_schemas_dir)
		os.environ['GCONF_CONFIG_SOURCE'] = commands.getstatusoutput('/usr/bin/gconftool-2 --get-default-source')[1]
		for schema in self.gconf_schemas:
			ofile = os.path.normpath(os.path.join(self.gconf_schemas_dir, schema))
			self.copy_file(schema, ofile)
		cmd = '/usr/bin/gconftool-2 --makefile-install-rule %s' % ofile
		err, out = commands.getstatusoutput(cmd)
		if out:
			self.announce(out)
		if err:
			self.warn("Error: installation of gconf schema files faield: " + out)

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
		('/usr/share/locale/ja/LC_MESSAGES', ['po/ja/pastie.mo']),
		('/usr/share/locale/ru/LC_MESSAGES', ['po/ru/pastie.mo']),
		('/usr/share/locale/uk/LC_MESSAGES', ['po/uk/pastie.mo']),
		('/usr/share/locale/it/LC_MESSAGES', ['po/it/pastie.mo'])
		],
	packages = ["pastielib"],
	cmdclass = {
		'install_gconf' : install_gconf,
		'install': pastie_install}, )
