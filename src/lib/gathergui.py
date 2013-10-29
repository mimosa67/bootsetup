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
  def __init__(self, version, bootloader = None, target_partition = None, is_test = False, use_test_data = False):
    self.cfg = Config(bootloader, target_partition, is_test, use_test_data)
    print """
bootloader         = {bootloader}
target partition   = {partition}
MBR device         = {mbr}
disks:{disks}
partitions:{partitions}
boot partitions:{boot_partitions}
""".format(bootloader = self.cfg.cur_bootloader, partition = self.cfg.cur_boot_partition, mbr = self.cfg.cur_mbr_device, disks = "\n - " + "\n - ".join(map(" ".join, self.cfg.disks)), partitions = "\n - " + "\n - ".join(map(" ".join, self.cfg.partitions)), boot_partitions = "\n - " + "\n - ".join(map(" ".join, self.cfg.boot_partitions)))
    builder = gtk.Builder()
    for d in ('./resources', '../resources'):
      if os.path.exists(d + '/bootsetup.glade'):
        builder.add_from_file(d + '/bootsetup.glade')
        break
    # Get a handle on the glade file widgets we want to interact with
    self.AboutDialog = builder.get_object("about_dialog")
    self.AboutDialog.set_version(version)
    self.AboutDialog.set_copyright(__copyright__)
    self.Window = builder.get_object("bootsetup_main")
    self.LabelContextHelp = builder.get_object("label_context_help")
    self.RadioLilo = builder.get_object("radiobutton_lilo")
    self.RadioGrub2 = builder.get_object("radiobutton_grub2")
    self.ComboBoxMbr = builder.get_object("combobox_mbr")
    self._add_combobox_cell_renderer(self.ComboBoxMbr, 1)
    self.LiloPart = builder.get_object("frame_lilo")
    self.Grub2Part = builder.get_object("hbox_grub2")
    self.ComboBoxPartition = builder.get_object("combobox_partition")
    self._add_combobox_cell_renderer(self.ComboBoxPartition, 2)
    self._add_combobox_cell_renderer(self.ComboBoxPartition, 1, padding=20)
    print "TODO"
    # Initialize the contextual help box
    self.context_intro = _("<b>BootSetup will install a new bootloader on your computer.</b> \n\
\n\
A bootloader is required to load the main operating system of a computer and will initially display \
a boot menu if several operating systems are available on the same computer.")
    self.on_leave_notify_event(None)
    self.build_data_stores()
    self.update_install_button()
    # Connect signals
    self.add_custom_signals()
    builder.connect_signals(self)

  def _add_combobox_cell_renderer(self, comboBox, modelPosition, start=False, expand=False, fill=True, padding=0):
    cell = gtk.CellRendererText()
    cell.set_property('xalign', 0)
    cell.set_property('xpad', padding)
    if start:
      comboBox.pack_start(cell, expand)
    else:
      comboBox.pack_end(cell, expand)
    comboBox.add_attribute(cell, 'text', modelPosition)

  # General contextual help
  def on_leave_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_markup(self.context_intro)

  def on_about_button_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_text(_("About BootSetup."))

  def on_boot_partition_treeview_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_markup(_("Here you must define a boot menu label for each \
of the operating system that will be displayed on your bootloader menu.\n\
Any partition for which you do not set a boot menu label will not be configured and will \
not be displayed on the bootloader menu.\n\
If a few kernels are available within one partition, the label you have chosen for that \
partition will be appended numerically to create multiple menu entries for each of these kernels.\n\
Any of these settings can be edited manually in the configuration file."))
  
  def on_up_eventbox_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_markup(_("Use this arrow if you want to move the \
selected Operating System up to a higher rank.\n\
The partition with the highest rank will be displayed on the first line of the bootloader menu.\n\
Any of these settings can be edited manually in the configuration file."))

  def on_down_eventbox_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_markup(_("Use this arrow if you want to move the \
selected Operating System down to a lower rank.\n\
The partition with the lowest rank will be displayed on the last line of the bootloader menu.\n\
Any of these settings can be edited manually in the configuration file."))

  def on_undo_eventbox_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_markup(_("This will undo all settings (even manual modifications)."))

  def on_edit_eventbox_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_markup(_("Experienced users have the possibility to \
manually edit the LiLo configuration file.\n\
Please do not temper with this file unless you know what you are doing and you have \
read its commented instructions regarding chrooted paths."))

  def on_button_quit_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_text(_("Exit BootSetup program."))

  def on_execute_eventbox_enter_notify_event(self, widget, data=None):
    self.LabelContextHelp.set_markup(_("Once you have defined your settings, \
click on this button to install your bootloader."))



  def build_data_stores(self):
    print 'Building choice lists…',
    sys.stdout.flush()
    print "TODO"
    print ' Done'
    sys.stdout.flush()

  # What to do when BootSetup logo is clicked
  def on_about_button_clicked(self, widget, data=None):
    self.AboutDialog.show()

  # What to do when the about dialog quit button is clicked
  def on_about_dialog_close(self, widget, data=None):
    self.AboutDialog.hide()
    return True

  # What to do when the exit X on the main window upper right is clicked
  def gtk_main_quit(self, widget, data=None):
    print "Bye _o/"
    gtk.main_quit()

  def on_bootloader_type_clicked(self, widget, data=None):
    if widget.get_active():
      if widget == self.RadioLilo:
        self.LiloPart.show()
        self.Grub2Part.hide()
      else:
        self.LiloPart.hide()
        self.Grub2Part.show()

  def update_install_button(self):
    print "TODO"
    #self.InstallButton.set_sensitive(not False in self.cfg.configurations.values())

  def add_custom_signals(self):
    print "TODO"
    #self.KeyboardList.get_selection().connect('changed', self.on_keyboard_list_changed_event)
    #self.LocaleList.get_selection().connect('changed', self.on_locale_list_changed_event)
  
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
    yes_callback()
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



  def on_combobox_mbr_changed(self, widget, data=None):
    print "TODO"
    pass

  def on_label_cellrenderercombo_edited(self, widget, data=None):
    print "TODO"
    pass

  def on_label_cellrenderercombo_editing_started(self, widget, data=None):
    print "TODO"
    pass

  def on_label_cellrenderercombo_editing_canceled(self, widget, data=None):
    print "TODO"
    pass

  def on_up_button_clicked(self, widget, data=None):
    print "TODO"
    pass

  def on_down_button_clicked(self, widget, data=None):
    print "TODO"
    pass

  def on_undo_button_clicked(self, widget, data=None):
    print "TODO"
    pass

  def on_edit_button_clicked(self, widget, data=None):
    print "TODO"
    pass

  def on_combobox_partition_changed(self, widget, data=None):
    print "TODO"
    pass

  def on_execute_button_clicked(self, widget, data=None):
    print "TODO"
    pass



  def on_install_button_clicked(self, widget, data=None):
    print "TODO"
    full_recap_msg = ''
    full_recap_msg += "\n<b>" + _("You are about to install Salix with the following settings:") + "</b>\n"
    self.show_yesno_dialog(full_recap_msg, self.setup_bootloader, None)
  def setup_bootloader(self):
    print "TODO"
    self.installation_umountall()
    self.installation_done()
  def installation_umountall(self):
    print "TODO"
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
