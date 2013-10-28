#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Graphical BootSetup configuration gathering.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import gettext
import gobject
import gtk
import gtk.glade
import re
import math
import subprocess
from common import *
from config import *
import salix_livetools_library as sltl

class GatherGui:
  """
  GUI to gather information about the configuration to setup.
  """
  def __init__(self, version, is_test = False, use_test_data = False):
    print "Init, Lilo by default"
    self.cfg = Config('lilo', is_test, use_test_data)
    builder = gtk.Builder()
    for d in ('./resources', '../resources'):
      if os.path.exists(d + '/bootsetup.glade'):
        builder.add_from_file(d + '/bootsetup.glade')
        break
    # Get a handle on the glade file widgets we want to interact with
    print "TODO"
    # TODO
    self.AboutDialog = builder.get_object("about_dialog")
    self.AboutDialog.set_version(version)
    self.Window = builder.get_object("main_window")
    # Initialize the contextual help box
    print "TODO"
    # TODO
    #self.context_intro = _("Contextual help.")
    self.on_leave_notify_event(None)
    self.build_data_stores()
    self.update_install_button()
    # Connect signals
    self.add_custom_signals()
    builder.connect_signals(self)

  # General contextual help
  def on_leave_notify_event(self, widget, data=None):
    print "TODO"
    # TODO
    #self.ContextLabel.set_text(self.context_intro)

  # What to do when Salix Installer logo is clicked
  def on_about_link_clicked(self, widget, data=None):
    self.AboutDialog.show()

  # What to do when the about dialog quit button is clicked
  def on_about_dialog_close(self, widget, data=None):
    self.AboutDialog.hide()
    return True

  # What to do when the exit X on the main window upper right is clicked
  def gtk_main_quit(self, widget, data=None):
    print "Bye _o/"
    gtk.main_quit()

  # What to do when the Salix Installer quit button is clicked
  def on_button_quit_clicked(self, widget, data=None):
    self.gtk_main_quit(widget)

  def build_data_stores(self):
    print 'Building choice lists…',
    sys.stdout.flush()
    print "TODO"
    # TODO
    print ' Done'
    sys.stdout.flush()

  def add_custom_signals(self):
    print "TODO"
    #self.KeyboardList.get_selection().connect('changed', self.on_keyboard_list_changed_event)
    #self.LocaleList.get_selection().connect('changed', self.on_locale_list_changed_event)

  def update_install_button(self):
    print "TODO"
    # TODO
    #self.InstallButton.set_sensitive(not False in self.cfg.configurations.values())
  
  def process_gui_events(self):
    """
    be sure to treat any pending GUI events before continue
    """
    while gtk.events_pending():
      gtk.main_iteration()
  
  def update_gui_async(self, fct, *args, **kwargs):
    gobject.idle_add(fct, *args, **kwargs)




  def show_yesno_dialog(self, msg, yes_callback, no_callback):
    print "TODO"
    #self.YesNoDialog.yes_callback = yes_callback
    #self.YesNoDialog.no_callback = no_callback
    #self.YesNoDialog.set_markup(msg)
    #self.YesNoDialog.show()
    #self.YesNoDialog.resize(1, 1) # ensure a correct size, by asking a recomputation
    yes_callback() # TODO
  def on_yesno_response(self, dialog, response_id, data=None):
    dialog.hide()
    self.process_gui_events()
    callback = None
    if response_id == gtk.RESPONSE_YES:
      callback = dialog.yes_callback
    elif response_id == gtk.RESPONSE_NO:
      callback = dialog.no_callback
    if callback:
      callback()



  def on_install_button_clicked(self, widget, data=None):
    print "TODO"
    # TODO
    full_recap_msg = ''
    full_recap_msg += "\n<b>" + _("You are about to install Salix with the following settings:") + "</b>\n"
    self.show_yesno_dialog(full_recap_msg, self.setup_bootloader, None)
  def setup_bootloader(self):
    print "TODO"
    # TODO
    self.installation_umountall()
    self.installation_done()
  def installation_umountall(self):
    print "TODO"
    # TODO
    # if not self.cfg.is_test:
    #   if self.cfg.linux_partitions:
    #     for p in self.cfg.linux_partitions:
    #       d = p[0]
    #       fulld = "/dev/{0}".format(d)
    #       if sltl.isMounted(fulld):
    #         sltl.umountDevice(fulld, deleteMountPoint = False)
    #   fulld = "/dev/{0}".format(self.cfg.main_partition)
    #   if sltl.isMounted(fulld):
    #     sltl.umountDevice(fulld)
  def installation_done(self):
    print "Bootloader Installation Done."
    msg = "<b>{0}</b>".format(_("Bootloader installation process completed..."))
    info_dialog(msg)
    self.gtk_main_quit(self.Window)
