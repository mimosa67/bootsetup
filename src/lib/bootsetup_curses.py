#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Curses BootSetup.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import os
import sys
import gettext
import re
from gathercurses import *
from bootsetup import *
import urwid
import urwid_wicd.curses_misc as urwicd

class BootSetupCurses(BootSetup):
  
  gc = None
  _palette = [
      ('important', 'yellow', 'black', 'bold'),
      ('info', 'white', 'dark blue', 'bold'),
      ('error', 'white', 'dark red', 'bold'),
    ]

  def run_setup(self):
    urwid.set_encoding('utf8')
    if os.getuid() != 0:
      self.error_dialog(_("Root privileges are required to run this program."), _("Sorry!"))
      sys.exit(1)
    self.gc = GatherCurses(self, self._version, self._bootloader, self._targetPartition, self._isTest, self._useTestData)
    self.gc.run()

  def info_dialog(self, message, title = None, parent = None):
    if not title:
      title = _("INFO")
    dialog = urwicd.TextDialog(('info', unicode(message)), 10, 60, ('important', unicode(title)))
    if self.gc:
      ui = self.gc._loop.screen
    else:
      ui = urwid.raw_display.Screen()
      ui.register_palette(self._palette)
      ui.start()
    if not parent:
      parent = urwid.Filler(urwid.Divider(), 'top')
    dialog.run(ui, parent)
    if not self.gc:
      ui.stop()

  def error_dialog(self, message, title = None, parent = None):
    if not title:
      title = _("/!\ ERROR")
    dialog = urwicd.TextDialog(('error', unicode(message)), 10, 60, ('important', unicode(title)))
    if self.gc:
      ui = self.gc._loop.screen
    else:
      ui = urwid.raw_display.Screen()
      ui.register_palette(self._palette)
      ui.start()
    if not parent:
      parent = urwid.Filler(urwid.Divider(), 'top')
    dialog.run(ui, parent)
    if not self.gc:
      ui.stop()
