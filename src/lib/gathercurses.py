#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Curses (urwid) BootSetup configuration gathering.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import gettext
import gobject
import urwid_more as urwidm
import re
import math
import subprocess
from config import *
import salix_livetools_library as sltl
from lilo import *
from grub2 import *

class GatherCurses:
  """
  UI in curses/urwid to gather information about the configuration to setup.
  """
  
  # Other potential color schemes can be found at:
  # http://excess.org/urwid/wiki/RecommendedPalette
  _palette = [
      ('body', 'light gray', 'black'),
      ('header', 'dark blue', 'light gray'),
      ('footer', 'light green', 'black', 'bold'),
      ('footer_key', 'yellow', 'black', 'bold'),
      ('strong', 'white', 'black', 'bold'),
      ('focusable', 'light green', 'black'),
      ('unfocusable', 'brown', 'black'),
      ('focus', 'black', 'light green'),
      ('focus_edit', 'yellow', 'black'),
      ('focus_icon', 'yellow', 'black'),
      ('focus_radio', 'yellow', 'black'),
      ('focus_combo', 'black', 'light green'),
      ('combobody', 'light gray', 'dark gray'),
      ('combofocus', 'black', 'yellow'),
      ('error', 'white', 'light red'),
      ('focus_error', 'light red', 'black'),
    ]
  _view = None
  _loop = None
  _labelPerDevice = {}
  _lilo = None
  _grub2 = None
  _editing = False
  _custom_lilo = False
  _liloMaxChars = 15

  def __init__(self, bootsetup, version, bootloader = None, target_partition = None, is_test = False, use_test_data = False):
    self._bootsetup = bootsetup
    self._version = version
    self.cfg = Config(bootloader, target_partition, is_test, use_test_data)
    print u"""
bootloader         = {bootloader}
target partition   = {partition}
MBR device         = {mbr}
disks:{disks}
partitions:{partitions}
boot partitions:{boot_partitions}
""".format(bootloader = self.cfg.cur_bootloader, partition = self.cfg.cur_boot_partition, mbr = self.cfg.cur_mbr_device, disks = "\n - " + "\n - ".join(map(" ".join, self.cfg.disks)), partitions = "\n - " + "\n - ".join(map(" ".join, self.cfg.partitions)), boot_partitions = "\n - " + "\n - ".join(map(" ".join, self.cfg.boot_partitions)))
    self.ui = urwidm.raw_display.Screen()
    self.ui.set_mouse_tracking()
    self._palette.extend(bootsetup._palette)
  
  def run(self):
    self._createView()
    self._changeBootloaderSection()
    self._loop = urwidm.MainLoop(self._view, self._palette, handle_mouse = True, unhandled_input = self._handleKeys, pop_ups = True)
    if self.cfg.cur_bootloader == 'lilo':
      self._radioLiLo.set_state(True)
    elif self.cfg.cur_bootloader == 'grub2':
      self._radioGrub2.set_state(True)
    self._loop.run()
  
  def _infoDialog(self, message):
    self._bootsetup.info_dialog(message, parent = self._view)

  def _errorDialog(self, message):
    self._bootsetup.error_dialog(message, parent = self._view)

  def _createComboBox(self, label, list):
    comboBox = urwidm.ComboBox(label, list)
    comboBox.set_combo_attrs('combobody', 'combofocus')
    comboBox.cbox.sensitive_attr = ('focusable', 'focus_combo')
    return comboBox
  
  def _createComboBoxEdit(self, label, list):
    comboBox = urwidm.ComboBoxEdit(label, list)
    comboBox.set_combo_attrs('combobody', 'combofocus')
    comboBox.cbox.sensitive_attr = ('focusable', 'focus_edit')
    return comboBox

  def _createEdit(self, caption = u'', edit_text = u'', multiline = False, align = 'left', wrap = 'space', allow_tab = False, edit_pos = None, layout = None, mask = None):
    edit = urwidm.EditMore(caption, edit_text, multiline, align, wrap, allow_tab, edit_pos, layout, mask)
    return edit

  def _createButton(self, label, on_press = None, user_data = None):
    btn = urwidm.ButtonMore(label, on_press, user_data)
    return btn

  def _createRadioButton(self, group, label, state = "first True", on_state_change = None, user_data = None):
    radio = urwidm.RadioButtonMore(group, label, state, on_state_change, user_data)
    return radio

  def _createCenterButtonsWidget(self, buttons, h_sep = 2, v_sep = 0):
    maxLen = 0
    for button in buttons:
      if not hasattr(button, 'get_label') and hasattr(button, 'original_widget'):
        button = button.original_widget
      maxLen = max(maxLen, len(button.get_label()))
    return urwidm.GridFlow(buttons, cell_width = maxLen + len('<  >'), h_sep = h_sep, v_sep = v_sep, align = "center")

  def _createView(self):
    """
+=======================================+
|                 Title                 |
+=======================================+
| Introduction text                     |
+---------------------------------------+
| Bootloader: (×) LiLo (_) Grub2        |
| MBR Device:  |_____________ ↓|        | <== ComboBox thanks to wicd
| Grub2 files: |_____________ ↓|        | <== Grub2 only
| +-----------------------------------+ | --+
| |Dev.|FS  |Type |Label      |Actions| |   |
| |sda1|ext4|Salix|Salix14____|<↑><↓> | |   |
| |sda5|xfs |Arch |ArchLinux__|<↑><↓> | |   +- <== LiLo only
| +-----------------------------------+ |   |
| <Edit config>    <Undo custom config> | --+
|            <Install>                  |
+=======================================+
| H: Help, A: About, Q: Quit            | <== Action keyboard thanks to wicd
+=======================================+
    """
    # header
    txtTitle = urwidm.Text(_("BootSetup curses, version {ver}").format(ver = self._version), align = "center")
    header = urwidm.PileMore([urwidm.Divider(), txtTitle, urwidm.Text('─' * (len(txtTitle.text) + 2), align = "center")])
    header.attr = 'header'
    # footer
    keys = [
        ('h', _("Help")),
        ('a', _("About")),
        (('q', 'f10'), _("Quit")),
      ]
    keysColumns = urwidm.OptCols(keys, self._handleKeys, attrs = ('footer_key', 'footer'))
    footer = urwidm.AttrMapMore(keysColumns, 'footer')
    # intro
    introHtml = _("<b>BootSetup will install a new bootloader on your computer.</b> \n\
\n\
A bootloader is required to load the main operating system of a computer and will initially display \
a boot menu if several operating systems are available on the same computer.")
    intro = map(lambda line: ('strong', line.replace("<b>", "").replace("</b>", "") + "\n") if line.startswith("<b>") else line, introHtml.split("\n"))
    intro[-1] = intro[-1].strip() # remove last "\n"
    txtIntro = urwidm.Text(intro)
    # bootloader type section
    lblBootloader = urwidm.Text(_("Bootloader:"))
    radioGroupBootloader = []
    self._radioLiLo = self._createRadioButton(radioGroupBootloader, "LiLo", state = False, on_state_change = self._onLiLoChange)
    self._radioGrub2 = self._createRadioButton(radioGroupBootloader, "Grub2", state = False, on_state_change = self._onGrub2Change)
    bootloaderTypeSection = urwidm.ColumnsMore([lblBootloader, self._radioLiLo, self._radioGrub2], focus_column = 1)
    # mbr device section
    mbrDeviceSection = self._createMbrDeviceSectionView()
    # bootloader section
    self._bootloaderSection = urwidm.WidgetPlaceholderMore(urwidm.Text(""))
    # install section
    btnInstall = self._createButton(_("_Install bootloader").replace("_", ""), on_press = self._onInstall)
    installSection = self._createCenterButtonsWidget([btnInstall])
    # body
    bodyList = [urwidm.Divider(), txtIntro, urwidm.Divider('─', bottom = 1), bootloaderTypeSection, mbrDeviceSection, urwidm.Divider(), self._bootloaderSection, urwidm.Divider('─', top = 1, bottom = 1), installSection]
    body = urwidm.ListBoxMore(urwidm.SimpleListWalker(bodyList))
    body.attr = 'body'
    frame = urwidm.FrameMore(body, header, footer, focus_part = 'body')
    frame.attr = 'body'
    self._view = frame

  def _createMbrDeviceSectionView(self):
    comboList = []
    for d in self.cfg.disks:
      comboList.append(" - ".join(d))
    comboBox = self._createComboBoxEdit(_("Install bootloader on:"), comboList)
    return comboBox

  def _createBootloaderSectionView(self):
    if self.cfg.cur_bootloader == 'lilo':
      listDevTitle = _("Partition")
      listFSTitle = _("File system")
      listLabelTitle = _("Boot menu label")
      listDev = [urwidm.Text(listDevTitle)]
      listFS = [urwidm.Text(listFSTitle)]
      listType = [urwidm.Text(_("Operating system"))]
      listLabel = [urwidm.Text(listLabelTitle)]
      listAction = [urwidm.Text("")]
      self._labelPerDevice = {}
      for p in self.cfg.boot_partitions:
        dev = p[0]
        fs = p[1]
        ostype = p[3]
        label = re.sub(r'[()]', '', re.sub(r'_\(loader\)', '', re.sub(' ', '_', p[4]))) # lilo does not like spaces and pretty print the label
        listDev.append(urwidm.Text(dev))
        listFS.append(urwidm.Text(fs))
        listType.append(urwidm.Text(ostype))
        self._labelPerDevice[dev] = label
        editLabel = self._createEdit(edit_text = label, wrap = urwidm.CLIP)
        urwidm.connect_signal(editLabel, 'change', self._onLabelChange, dev)
        urwidm.connect_signal(editLabel, 'focuslost', self._onLabelFocusLost, dev)
        listLabel.append(editLabel)
        listAction.append(urwidm.GridFlowMore([self._createButton("↑", on_press = self._moveLineUp, user_data = p[0]), self._createButton("↓", on_press = self._moveLineDown, user_data = p[0])], cell_width = 5, h_sep = 1, v_sep = 1, align = "center"))
      colDev = urwidm.PileMore(listDev)
      colFS = urwidm.PileMore(listFS)
      colType = urwidm.PileMore(listType)
      colLabel = urwidm.PileMore(listLabel)
      colAction = urwidm.PileMore(listAction)
      self._liloTable = urwidm.ColumnsMore([('fixed', max(6, len(listDevTitle)), colDev), ('fixed', max(6, len(listFSTitle)), colFS), colType, ('fixed', max(self._liloMaxChars + 1, len(listLabelTitle)), colLabel), ('fixed', 11, colAction)], dividechars = 1)
      table = urwidm.LineBoxMore(self._liloTable)
      btnEdit = self._createButton(_("_Edit configuration").replace("_", ""), on_press = self._editLiLoConf)
      btnCancel = self._createButton(_("_Undo configuration").replace("_", ""), on_press = self._cancelLiLoConf)
      pile = urwidm.PileMore([table, self._createCenterButtonsWidget([btnEdit, btnCancel])])
      return pile
    elif self.cfg.cur_bootloader == 'grub2':
      comboList = []
      for p in self.cfg.partitions:
        comboList.append(" - ".join(p))
      comboBox = self._createComboBox(_("Install Grub2 files on:"), comboList)
      return comboBox
    else:
      return urwidm.Text("")

  def _changeBootloaderSection(self):
    self._bootloaderSection.original_widget = self._createBootloaderSectionView()

  def _handleKeys(self, key):
    if not isinstance(key, tuple): # only keyboard input
      if key.lower() in ('q', 'f10'):
        self.main_quit()

  def _onLiLoChange(self, radioLiLo, newState):
    if newState:
      self.cfg.cur_bootloader = 'lilo'
      if self._grub2:
        self._grub2 = None
      self._lilo = Lilo(self.cfg.is_test)
      self._changeBootloaderSection()

  def _onGrub2Change(self, radioGrub2, newState):
    if newState:
      self.cfg.cur_bootloader = 'grub2'
      if self._lilo:
        self._lilo = None
      self._grub2 = Grub2(self.cfg.is_test)
      self._changeBootloaderSection()

  def _isLabelValid(self, label):
    if ' ' in label:
      return 'space'
    elif len(label) > self._liloMaxChars:
      return 'max'
    else:
      return 'ok'
  def _showLabelError(self, errorType, editLabel):
    """Show a label error if the errorType is 'space' or 'max' and return True, else return False."""
    if errorType == 'space':
      self._bootsetup.error_dialog(_("\nAn Operating System label should not contain spaces.\n\nPlease verify and correct.\n"))
      editLabel.sensitive_attr = ('error', 'focus_error')
      return True
    elif errorType == 'max':
      self._bootsetup.error_dialog(_("\nAn Operating System label should not hold more than {max} characters.\n\nPlease verify and correct.\n".format(max = self._liloMaxChars)))
      editLabel.sensitive_attr = ('error', 'focus_error')
      return True
    elif errorType == 'pass':
      return False
    else: # == 'ok'
      editLabel.sensitive_attr = ('focusable', 'focus_edit')
      return False
  def _onLabelChange(self, editLabel, newText, device):
    validOld = self._isLabelValid(editLabel.edit_text)
    if validOld == 'ok':
      validNew = self._isLabelValid(newText)
    else:
      validNew = 'pass'
    if not self._showLabelError(validNew, editLabel):
      self._labelPerDevice[device] = newText
  def _onLabelFocusLost(self, editLabel, device):
    return not self._showLabelError(self._isLabelValid(editLabel.edit_text), editLabel)

  def _findDevPosition(self, device):
    colDevice = self._liloTable.widget_list[0]
    for i, line in enumerate(colDevice.widget_list):
      if i == 0: # skip header
        continue
      if line.text == device:
        return i
    return None

  def _moveLineUp(self, button, device):
    pos = self._findDevPosition(device)
    if pos > 1: # 0 = header
      for col, types in self._liloTable.contents:
        old = col.widget_list[pos]
        del col.widget_list[pos]
        col.widget_list.insert(pos - 1, old)

  def _moveLineDown(self, button, device):
    pos = self._findDevPosition(device)
    if pos < len(self._liloTable.widget_list[0].item_types) - 1:
      for col, types in self._liloTable.contents:
        old = col.widget_list[pos]
        del col.widget_list[pos]
        col.widget_list.insert(pos + 1, old)

  def _create_lilo_config(self):
    partitions = []
    self.cfg.cur_boot_partition = None
    for p in self.cfg.boot_partitions:
      dev = p[0]
      fs = p[1]
      t = p[2]
      label = self._labelPerDevice[dev]
      if not self.cfg.cur_boot_partition and t == 'linux':
        self.cfg.cur_boot_partition = dev
      partitions.append([dev, fs, t, label])
    if self.cfg.cur_boot_partition:
      self._lilo.createConfiguration(self.cfg.cur_mbr_device, self.cfg.cur_boot_partition, partitions)
    else:
      self._bootsetup.error_dialog(_("Sorry, BootSetup is unable to find a Linux filesystem on your choosen boot entries, so cannot install LiLo.\n"))

  def _editLiLoConf(self, button):
    lilocfg = self._lilo.getConfigurationPath()
    if not os.path.exists(lilocfg):
      self._custom_lilo = True
      self._create_lilo_config()
    if os.path.exists(lilocfg):
      launched = False
      for editor in ('vim', 'nano'):
        try:
          sltl.execCall([editor, lilocfg], shell=False, env=None)
          launched = True
          break
        except:
          pass
      if not launched:
        self._bootsetup.error_dialog(_("Sorry, BootSetup is unable to find a suitable text editor in your system. You will not be able to manually modify the LiLo configuration.\n"))

  def _cancelLiLoConf(self, button):
    lilocfg = self._lilo.getConfigurationPath()
    if os.path.exists(lilocfg):
      os.remove(lilocfg)
    self._custom_lilo = False

  def _onInstall(self, btnInstall):
    if self.cfg.cur_bootloader == 'lilo':
      if not os.path.exists(self._lilo.getConfigurationPath()):
        self._create_lilo_config()
      self._lilo.install()
    elif self.cfg.cur_bootloader == 'grub2':
      self._grub2.install(self.cfg.cur_mbr_device, self.cfg.cur_boot_partition)
    self.installation_done()

  def installation_done(self):
    print "Bootloader Installation Done."
    msg = _("Bootloader installation process completed.")
    self._bootsetup.info_dialog(msg)
    self.main_quit()

  def main_quit(self):
    if self._lilo:
      del self._lilo
    if self._grub2:
      del self._grub2
    print "Bye _o/"
    raise urwidm.ExitMainLoop()
