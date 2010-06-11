#!/usr/bin/env python
from py2deb import Py2deb

version = "0.2.2"

p = Py2deb("pastie")
p.author = "Felipe Morales"
p.mail = "hel.sheep@gmail.com"
p.description = "A simple appindicator based clipboard manager."
p.depends = "python-appindicator"
p.license = "gpl"
p.section = "x11"
p.arch = "all"

p["/usr/bin"] = ["pastie.py|pastie"]
p["/usr/lib/python2.6/dist-packages"] = ["pastie/history.py", "pastie/__init__.py", "pastie/protector.py", "pastie/edit_clipboard.py"]
p["/usr/share/applications"] = ["pastie.desktop"]
p["/usr/share/locale/es/LC_MESSAGES"] = ["po/pastie.es.mo|pastie.mo"]

p.generate(version)
