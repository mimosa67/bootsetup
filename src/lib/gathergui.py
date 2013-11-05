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
from lilo import *
from grub2 import *

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
    self.ComboBoxMbrEntry = self.ComboBoxMbr.get_internal_child(builder, "entry")
    self._add_combobox_cell_renderer(self.ComboBoxMbr, 1)
    self.LiloPart = builder.get_object("part_lilo")
    self.BootPartitionTreeview = builder.get_object("boot_partition_treeview")
    self.LabelCellRendererCombo = builder.get_object("label_cellrenderercombo")
    self.PartitionTreeViewColumn = builder.get_object("partition_treeviewcolumn")
    self.FileSystemTreeViewColumn = builder.get_object("filesystem_treeviewcolumn")
    self.OsTreeViewColumn = builder.get_object("os_treeviewcolumn")
    self.LabelTreeViewColumn = builder.get_object("label_treeviewcolumn")
    self.UpButton = builder.get_object("up_button")
    self.DownButton = builder.get_object("down_button")
    self.UndoButton = builder.get_object("undo_button")
    self.EditButton = builder.get_object("edit_button")
    self.Grub2Part = builder.get_object("part_grub2")
    self.ComboBoxPartition = builder.get_object("combobox_partition")
    self.ComboBoxPartitionEntry = self.ComboBoxPartition.get_internal_child(builder, "entry")
    self._add_combobox_cell_renderer(self.ComboBoxPartition, 2)
    self._add_combobox_cell_renderer(self.ComboBoxPartition, 1, padding=20)
    self.ExecuteButton = builder.get_object("execute_button")
    self.DiskListStore = builder.get_object("boot_disk_list_store")
    self.PartitionListStore = builder.get_object("boot_partition_list_store")
    self.BootPartitionListStore = builder.get_object("boot_bootpartition_list_store")
    self.BootLabelListStore = builder.get_object("boot_label_list_store")
    # Initialize the contextual help box
    self.context_intro = _("<b>BootSetup will install a new bootloader on your computer.</b> \n\
\n\
A bootloader is required to load the main operating system of a computer and will initially display \
a boot menu if several operating systems are available on the same computer.")
    self.on_leave_notify_event(None)
    self.editing = False
    self.custom_lilo = False
    self.lilo = self.grub2 = None
    self.build_data_stores()
    self.update_buttons()
    # Connect signals
    builder.connect_signals(self)

  def _add_combobox_cell_renderer(self, comboBox, modelPosition, start=False, expand=False, padding=0):
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
    if self.cfg.cur_bootloader == 'lilo':
      self.RadioLilo.activate()
      self.Window.set_focus(self.RadioLilo)
    elif self.cfg.cur_bootloader == 'grub2':
      self.RadioGrub2.activate()
      self.Window.set_focus(self.RadioGrub2)
    self.DiskListStore.clear()
    self.PartitionListStore.clear()
    self.BootPartitionListStore.clear()
    for d in self.cfg.disks:
      self.DiskListStore.append(d)
    for p in self.cfg.partitions: # for grub2
      self.PartitionListStore.append(p)
    for p in self.cfg.boot_partitions: # for lilo
      p2 = list(p) # copy p
      del p2[2] # discard boot type
      p2[3] = re.sub(r'[()]', '', re.sub(r'_\(loader\)', '', re.sub(' ', '_', p2[3]))) # lilo does not like spaces and pretty print the label
      p2.append('gtk-edit') # add a visual
      self.BootPartitionListStore.append(p2)
    self.ComboBoxMbrEntry.set_text(self.cfg.cur_mbr_device)
    self.ComboBoxPartitionEntry.set_text(self.cfg.cur_boot_partition)
    self.LabelCellRendererCombo.set_property("model", self.BootLabelListStore)
    self.LabelCellRendererCombo.set_property('text-column', 0)
    self.LabelCellRendererCombo.set_property('editable', True)
    self.LabelCellRendererCombo.set_property('cell_background', '#CCCCCC')
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
    del self.lilo
    del self.grub2
    print "Bye _o/"
    gtk.main_quit()

  def process_gui_events(self):
    """
    be sure to treat any pending GUI events before continue
    """
    while gtk.events_pending():
      gtk.main_iteration()

  def update_gui_async(self, fct, *args, **kwargs):
    gobject.idle_add(fct, *args, **kwargs)

  def on_bootloader_type_clicked(self, widget, data=None):
    if widget.get_active():
      if widget == self.RadioLilo:
        self.cfg.cur_bootloader = 'lilo'
        if self.grub2:
          del self.grub2
        self.lilo = Lilo(self.cfg.is_test)
        self.LiloPart.show()
        self.Grub2Part.hide()
      else:
        self.cfg.cur_bootloader = 'grub2'
        if self.lilo:
          del self.lilo
        self.grub2 = Grub2(self.cfg.is_test)
        self.LiloPart.hide()
        self.Grub2Part.show()
      self.update_buttons()

  def on_combobox_mbr_changed(self, widget, data=None):
    self.cfg.cur_mbr_device = self.ComboBoxMbrEntry.get_text()
    self.update_buttons()

  def set_editing_mode(self, is_edit):
    self.editing = is_edit
    self.update_buttons()

  def on_label_cellrenderercombo_editing_started(self, widget, path, data):
    self.set_editing_mode(True)

  def on_label_cellrenderercombo_editing_canceled(self, widget):
    self.set_editing_mode(False)

  def on_label_cellrenderercombo_edited(self, widget, row_number, new_text):
    row_number = int(row_number)
    max_chars = 15
    if ' ' in new_text:
      error_dialog(_("\nAn Operating System label should not contain any space.\n\nPlease verify and correct.\n"))
    elif len(new_text) > max_chars:
      error_dialog(_("\nAn Operating System label should not hold more than {max} characters.\n\nPlease verify and correct.\n".format(max=max_chars)))
    else:
      model, it = self.BootPartitionTreeview.get_selection().get_selected()
      found = False
      for i, line in enumerate(model):
        if i == row_number or line[3] == _("Set..."):
          continue
        if line[3] == new_text:
          found = True
          break
      if found:
        error_dialog(_("You have used the same label for different Operating Systems. Please verify and correct.\n"))
      else:
        model.set_value(it, 3, new_text)
        if new_text == _("Set..."):
          model.set_value(it, 4, "gtk-edit")
        else:
          model.set_value(it, 4, "gtk-yes")
    self.set_editing_mode(False)

  def on_up_button_clicked(self, widget, data=None):
    """
    Move the row items upward.

    """
    # Obtain selection
    sel = self.BootPartitionTreeview.get_selection()
    # Get selected path
    (model, rows) = sel.get_selected_rows()
    if not rows:
      return
    # Get new path for each selected row and swap items.
    for path1 in rows:
      # Move path2 upward
      path2 = (path1[0] - 1,)
    # If path2 is negative, the user tried to move first path up.
    if path2[0] < 0:
      return
    # Obtain iters and swap items.
    iter1 = model.get_iter(path1)
    iter2 = model.get_iter(path2)
    model.swap(iter1, iter2)

  def on_down_button_clicked(self, widget, data=None):
    """
    Move the row items downward.

    """
    # Obtain selection
    sel = self.BootPartitionTreeview.get_selection()
    # Get selected path
    (model, rows) = sel.get_selected_rows()
    if not rows:
      return
    # Get new path for each selected row and swap items.
    for path1 in rows:
      # Move path2 downward
      path2 = (path1[0] + 1,)
    # If path2 is negative, we're trying to move first path up.
    if path2[0] < 0:
      return
    # Obtain iters and swap items.
    iter1 = model.get_iter(path1)
    # If the second iter is invalid, the user tried to move the last item down.
    try:
      iter2 = model.get_iter(path2)
    except ValueError:
      return
    model.swap(iter1, iter2)

  def _create_lilo_config(self):
    partitions = []
    self.cfg.cur_boot_partition = None
    for row in self.BootPartitionListStore:
      p = list(row)
      if p[4] == "gtk-yes":
        dev = p[0]
        fs = p[1]
        t = "chain"
        for p2 in self.cfg.boot_partitions:
          if p2[0] == dev:
            t = p2[2]
            break
        label = p[3]
        if not self.cfg.cur_boot_partition and t == 'linux':
          self.cfg.cur_boot_partition = dev
        partitions.append([dev, fs, t, label])
    if self.cfg.cur_boot_partition:
      self.lilo.createConfiguration(self.cfg.cur_mbr_device, self.cfg.cur_boot_partition, partitions)
    else:
      error_dialog(_("Sorry, BootSetup is unable to find a Linux filesystem on your choosen boot entries, so cannot install LiLo.\n"))

  def on_edit_button_clicked(self, widget, data=None):
    lilocfg = self.lilo.getConfigurationPath()
    if not os.path.exists(lilocfg):
      self.custom_lilo = True
      self.update_buttons()
      self._create_lilo_config()
    if os.path.exists(lilocfg):
      try:
        sltl.execCall(['xdg-open', lilocfg], shell=False, env=None)
      except:
        error_dialog(_("Sorry, BootSetup is unable to find a suitable text editor in your system. You will not be able to manually modify the LiLo configuration.\n"))

  def on_undo_button_clicked(self, widget, data=None):
    lilocfg = self.lilo.getConfigurationPath()
    if os.path.exists(lilocfg):
      os.remove(lilocfg)
    self.custom_lilo = False
    self.update_buttons()

  def on_combobox_partition_changed(self, widget, data=None):
    self.cfg.cur_boot_partition = self.ComboBoxPartitionEntry.get_text()
    self.update_buttons()

  def update_buttons(self):
    install_ok = False
    multiple = False
    if self.cfg.cur_mbr_device and os.path.exists("/dev/{0}".format(self.cfg.cur_mbr_device)) and sltl.getDiskInfo(self.cfg.cur_mbr_device):
      if self.cfg.cur_bootloader == 'lilo' and not self.editing:
        if len(self.BootPartitionListStore) > 1:
          multiple = True
        for bp in self.BootPartitionListStore:
          if bp[4] == "gtk-yes":
            install_ok = True
      elif self.cfg.cur_bootloader == 'grub2':
        if self.cfg.cur_boot_partition and os.path.exists("/dev/{0}".format(self.cfg.cur_boot_partition)) and sltl.getPartitionInfo(self.cfg.cur_boot_partition):
          install_ok = True
    self.RadioLilo.set_sensitive(not self.editing)
    self.RadioGrub2.set_sensitive(not self.editing)
    self.ComboBoxMbr.set_sensitive(not self.editing)
    self.BootPartitionTreeview.set_sensitive(not self.custom_lilo)
    self.UpButton.set_sensitive(not self.editing and multiple)
    self.DownButton.set_sensitive(not self.editing and multiple)
    self.UndoButton.set_sensitive(not self.editing and self.custom_lilo)
    self.EditButton.set_sensitive(not self.editing and install_ok)
    self.ExecuteButton.set_sensitive(not self.editing and install_ok)

  def on_execute_button_clicked(self, widget, data=None):
    if self.cfg.cur_bootloader == 'lilo':
      if not os.path.exists(self.lilo.getConfigurationPath()):
        self._create_lilo_config()
      self.lilo.install()
    elif self.cfg.cur_bootloader == 'grub2':
      self.grub2.install(self.cfg.cur_mbr_device, self.cfg.cur_boot_partition)
    self.installation_done()

  def installation_done(self):
    print "Bootloader Installation Done."
    msg = "<b>{0}</b>".format(_("Bootloader installation process completed..."))
    info_dialog(msg)
    self.gtk_main_quit(self.Window)
