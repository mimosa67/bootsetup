#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Graphical BootSetup.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import os
import sys
import gettext
import gtk
import gtk.glade
from bootsetup import *
from gathergui import *

class BootSetupGtk(BootSetup):
  def run_setup(self):
    gtk.glade.bindtextdomain(self._appName, self._localeDir)
    gtk.glade.textdomain(self._appName)
    if not (self._isTest and self._useTestData) and os.getuid() != 0:
      self.error_dialog(_("Root privileges are required to run this program."), _("Sorry!"))
      sys.exit(1)
    gg = GatherGui(self, self._version, self._bootloader, self._targetPartition, self._isTest, self._useTestData)
    gg.run()
  
  def info_dialog(self, message, title = None, parent = None):
    dialog = gtk.MessageDialog(parent = parent, type = gtk.MESSAGE_INFO, buttons = gtk.BUTTONS_OK, flags = gtk.DIALOG_MODAL)
    if title:
      msg = u"<b>{0}</b>\n\n{1}".format(unicode(title), unicode(message))
    else:
      msg = message
    dialog.set_markup(msg)
    result_info = dialog.run()
    dialog.destroy()
    return result_info

  def error_dialog(self, message, title = None, parent = None):
    dialog = gtk.MessageDialog(parent = parent, type = gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_CLOSE, flags = gtk.DIALOG_MODAL)
    if title:
      msg = u"<b>{0}</b>\n\n{1}".format(unicode(title), unicode(message))
    else:
      msg = message
    dialog.set_markup(msg)
    result_error = dialog.run()
    dialog.destroy()
    return result_error
