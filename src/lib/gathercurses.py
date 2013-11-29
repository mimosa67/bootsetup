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
      ('header', 'white', 'dark blue'),
      ('footer', 'light green', 'black'),
      ('footer_key', 'yellow', 'black'),
      ('strong', 'white', 'black'),
      ('copyright', 'light blue', 'black'),
      ('authors', 'light cyan', 'black'),
      ('translators', 'light green', 'black'),
      ('focusable', 'light green', 'black'),
      ('unfocusable', 'dark blue', 'black'),
      ('focus', 'black', 'dark green'),
      ('focus_edit', 'yellow', 'black'),
      ('focus_icon', 'yellow', 'black'),
      ('focus_radio', 'yellow', 'black'),
      ('focus_combo', 'black', 'dark green'),
      ('combobody', 'light gray', 'dark blue'),
      ('combofocus', 'black', 'brown'),
      ('error', 'white', 'dark red'),
      ('focus_error', 'light red', 'black'),
    ]
  _mainView = None
  _helpView = None
  _aboutView = None
  _mode = 'main'
  _loop = None
  _helpCtx = ''
  _labelPerDevice = {}
  _lilo = None
  _grub2 = None
  _editing = False
  _custom_lilo = False
  _grub2_cfg = False
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
    self._createMainView()
    self._createHelpView()
    self._createAboutView()
    self._changeBootloaderSection()
    self._loop = urwidm.MainLoop(self._mainView, self._palette, handle_mouse = True, unhandled_input = self._handleKeys, pop_ups = True)
    if self.cfg.cur_bootloader == 'lilo':
      self._radioLiLo.set_state(True)
      self._mainView.body.set_focus(self._mbrDeviceSectionPosition)
    elif self.cfg.cur_bootloader == 'grub2':
      self._radioGrub2.set_state(True)
      self._mainView.body.set_focus(self._mbrDeviceSectionPosition)
    self._loop.run()
  
  def _infoDialog(self, message):
    self._bootsetup.info_dialog(message, parent = self._loop.widget)

  def _errorDialog(self, message):
    self._bootsetup.error_dialog(message, parent = self._loop.widget)

  def _updateScreen(self):
    if self._loop and self._loop.screen._started:
      self._loop.draw_screen()
    
  def _onHelpFocusGain(self, widget, context):
    print "help context", context, widget
    raw_input("")
    self._helpCtx = context
    return True
  def _onHelpFocusLost(self, widget):
    self._helpCtx = ''
    return True

  def _createComboBox(self, label, elements):
    l = [urwidm.TextMultiValues(el) if isinstance(el, list) else el for el in elements]
    comboBox = urwidm.ComboBox(label, l)
    comboBox.set_combo_attrs('combobody', 'combofocus')
    comboBox.cbox.sensitive_attr = ('focusable', 'focus_combo')
    return comboBox
  
  def _createComboBoxEdit(self, label, elements):
    l = [urwidm.TextMultiValues(el) if isinstance(el, list) else el for el in elements]
    comboBox = urwidm.ComboBoxEdit(label, l)
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
    maxLen = reduce(max, [len(b.label) for b in buttons], 0) + len(u"<  >")
    return urwidm.GridFlowMore(buttons, maxLen, h_sep, v_sep, "center")

  def _createMainView(self):
    """
+=======================================+
|                 Title                 |
+=======================================+
| Introduction text                     |
+---------------------------------------+
| Bootloader: (×) LiLo (_) Grub2        |
| MBR Device:  |_____________ ↓|        | <== ComboBox thanks to wicd
| Grub2 files: |_____________ ↓|        | --|
|           <Edit config>               | --+- <== Grub2 only
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
    txtTitle = urwidm.Text(_(u"BootSetup curses, version {ver}").format(ver = self._version), align = "center")
    header = urwidm.PileMore([urwidm.Divider(), txtTitle, urwidm.Text('─' * (len(txtTitle.text) + 2), align = "center")])
    header.attr = 'header'
    # footer
    keys = [
        (('h', 'f2'), _("Help")),
        (('a', 'ctrl a'), _("About")),
        (('q', 'f10'), _("Quit")),
      ]
    keysColumns = urwidm.OptCols(keys, self._handleKeys, attrs = ('footer_key', 'footer'))
    keysColumns.attr = 'footer'
    footer = urwidm.PileMore([urwidm.Divider(u'⎽'), keysColumns])
    footer.attr = 'footer'
    # intro
    introHtml = _(u"<b>BootSetup will install a new bootloader on your computer.</b> \n\
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
    urwidm.connect_signal(bootloaderTypeSection, 'focusgain', self._onHelpFocusGain, 'type')
    urwidm.connect_signal(bootloaderTypeSection, 'focuslost', self._onHelpFocusLost)
    # mbr device section
    mbrDeviceSection = self._createMbrDeviceSectionView()
    # bootloader section
    self._bootloaderSection = urwidm.WidgetPlaceholderMore(urwidm.Text(""))
    # install section
    btnInstall = self._createButton(_("_Install bootloader").replace("_", ""), on_press = self._onInstall)
    urwidm.connect_signal(btnInstall, 'focusgain', self._onHelpFocusGain, 'install')
    urwidm.connect_signal(btnInstall, 'focuslost', self._onHelpFocusLost)
    installSection = self._createCenterButtonsWidget([btnInstall])
    # body
    bodyList = [urwidm.Divider(), txtIntro, urwidm.Divider('─', bottom = 1), bootloaderTypeSection, mbrDeviceSection, urwidm.Divider(), self._bootloaderSection, urwidm.Divider('─', top = 1, bottom = 1), installSection]
    self._mbrDeviceSectionPosition = 4
    body = urwidm.ListBoxMore(urwidm.SimpleListWalker(bodyList))
    body.attr = 'body'
    frame = urwidm.FrameMore(body, header, footer, focus_part = 'body')
    frame.attr = 'body'
    self._mainView = frame
  
  def _createHelpView(self):
    bodyPile = urwidm.PileMore([urwidm.Divider(), urwidm.TextMore(u"Help")])
    bodyPile.attr = 'body'
    body = urwidm.FillerMore(bodyPile, valign = "top")
    body.attr = 'body'
    txtTitle = urwidm.Text(_(u"Help"), align = "center")
    header = urwidm.PileMore([urwidm.Divider(), txtTitle, urwidm.Text('─' * (len(txtTitle.text) + 2), align = "center")])
    header.attr = 'header'
    keys = [
        (('q', 'esc', 'enter'), _("Close")),
      ]
    keysColumns = urwidm.OptCols(keys, self._handleKeys, attrs = ('footer_key', 'footer'))
    keysColumns.attr = 'footer'
    footer = urwidm.PileMore([urwidm.Divider(u'⎽'), keysColumns])
    footer.attr = 'footer'
    frame = urwidm.FrameMore(body, header, footer, focus_part = 'body')
    frame.attr = 'body'
    self._helpView = frame

  def _createAboutView(self):
    divider = urwidm.Divider()
    name = urwidm.TextMore(('strong', _(u"BootSetup curses, version {ver}").format(ver = self._version)), align = "center")
    comments = urwidm.TextMore(('body', _(u"Helps set up a bootloader like LiLo or Grub2.")), align = "center")
    copyright = urwidm.TextMore(('copyright', u"Copyright © 2013-2014 Salix OS"), align = "center")
    license = urwidm.TextMore(('copyright', u"GPL v2+"), align = "center")
    url = urwidm.TextMore(('strong', u"http://salixos.org"), align = "center")
    authors = urwidm.TextMore(('authors', _(u"Authors:") + "\n" + _(u"Cyrille Pontvieux <jrd~at~enialis~dot~net>\nPierrick Le Brun <akuna~at~salixos~dot~org>")), align = "center")
    translators = urwidm.TextMore(('translators', _(u"Translators:") + "\n" + _(u"translator_name <translator@email.com>")), align = "center")
    bodyPile = urwidm.PileMore([divider, name, comments, divider, copyright, license, divider, url, divider, authors, translators])
    bodyPile.attr = 'body'
    body = urwidm.FillerMore(bodyPile, valign = "top")
    body.attr = 'body'
    txtTitle = urwidm.Text(_(u"About BootSetup"), align = "center")
    header = urwidm.PileMore([urwidm.Divider(), txtTitle, urwidm.Text('─' * (len(txtTitle.text) + 2), align = "center")])
    header.attr = 'header'
    keys = [
        (('q', 'esc', 'enter'), _("Close")),
      ]
    keysColumns = urwidm.OptCols(keys, self._handleKeys, attrs = ('footer_key', 'footer'))
    keysColumns.attr = 'footer'
    footer = urwidm.PileMore([urwidm.Divider(u'⎽'), keysColumns])
    footer.attr = 'footer'
    frame = urwidm.FrameMore(body, header, footer, focus_part = 'body')
    frame.attr = 'body'
    self._aboutView = frame

  def _createMbrDeviceSectionView(self):
    comboBox = self._createComboBoxEdit(_("Install bootloader on:"), self.cfg.disks)
    urwidm.connect_signal(comboBox, 'change', self._onMBRChange)
    urwidm.connect_signal(comboBox, 'focusgain', self._onHelpFocusGain, 'mbr')
    urwidm.connect_signal(comboBox, 'focuslost', self._onHelpFocusLost)
    return comboBox

  def _createBootloaderSectionView(self):
    if self.cfg.cur_bootloader == 'lilo':
      listDevTitle = _("Partition")
      listFSTitle = _("File system")
      listLabelTitle = _("Boot menu label")
      listDev = [urwidm.TextMore(listDevTitle)]
      listFS = [urwidm.TextMore(listFSTitle)]
      listType = [urwidm.TextMore(_("Operating system"))]
      listLabel = [urwidm.TextMore(listLabelTitle)]
      listAction = [urwidm.TextMore("")]
      for l in (listDev, listFS, listType, listLabel, listAction):
        l[0].sensitive_attr = 'strong'
      self._labelPerDevice = {}
      for p in self.cfg.boot_partitions:
        dev = p[0]
        fs = p[1]
        ostype = p[3]
        label = re.sub(r'[()]', '', re.sub(r'_\(loader\)', '', re.sub(' ', '_', p[4]))) # lilo does not like spaces and pretty print the label
        listDev.append(urwidm.TextMore(dev))
        listFS.append(urwidm.TextMore(fs))
        listType.append(urwidm.TextMore(ostype))
        self._labelPerDevice[dev] = label
        editLabel = self._createEdit(edit_text = label, wrap = urwidm.CLIP)
        urwidm.connect_signal(editLabel, 'change', self._onLabelChange, dev)
        urwidm.connect_signal(editLabel, 'focuslost', self._onLabelFocusLost, dev)
        urwidm.connect_signal(editLabel, 'focusgain', self._onHelpFocusGain, 'lilotable')
        urwidm.connect_signal(editLabel, 'focuslost', self._onHelpFocusLost)
        listLabel.append(editLabel)
        btnUp = self._createButton("↑", on_press = self._moveLineUp, user_data = p[0])
        btnDown = self._createButton("↓", on_press = self._moveLineDown, user_data = p[0])
        urwidm.connect_signal(btnUp, 'focusgain', self._onHelpFocusGain, 'liloup')
        urwidm.connect_signal(btnUp, 'focuslost', self._onHelpFocusLost)
        urwidm.connect_signal(btnDown, 'focusgain', self._onHelpFocusGain, 'lilodown')
        urwidm.connect_signal(btnDown, 'focuslost', self._onHelpFocusLost)
        listAction.append(urwidm.GridFlowMore([btnUp, btnDown], cell_width = 5, h_sep = 1, v_sep = 1, align = "center"))
      colDev = urwidm.PileMore(listDev)
      colFS = urwidm.PileMore(listFS)
      colType = urwidm.PileMore(listType)
      colLabel = urwidm.PileMore(listLabel)
      colAction = urwidm.PileMore(listAction)
      self._liloTable = urwidm.ColumnsMore([('fixed', max(6, len(listDevTitle)), colDev), ('fixed', max(6, len(listFSTitle)), colFS), colType, ('fixed', max(self._liloMaxChars + 1, len(listLabelTitle)), colLabel), ('fixed', 11, colAction)], dividechars = 1)
      self._liloTableLines = urwidm.LineBoxMore(self._liloTable)
      self._liloTableLines.sensitive_attr = "strong"
      self._liloTableLines.unsensitive_attr = "unfocusable"
      self._liloBtnEdit = self._createButton(_("_Edit configuration").replace("_", ""), on_press = self._editLiLoConf)
      urwidm.connect_signal(self._liloBtnEdit, 'focusgain', self._onHelpFocusGain, 'liloedit')
      urwidm.connect_signal(self._liloBtnEdit, 'focuslost', self._onHelpFocusLost)
      self._liloBtnCancel = self._createButton(_("_Undo configuration").replace("_", ""), on_press = self._cancelLiLoConf)
      urwidm.connect_signal(self._liloBtnCancel, 'focusgain', self._onHelpFocusGain, 'lilocancel')
      urwidm.connect_signal(self._liloBtnCancel, 'focuslost', self._onHelpFocusLost)
      self._liloButtons = self._createCenterButtonsWidget([self._liloBtnEdit, self._liloBtnCancel])
      pile = urwidm.PileMore([self._liloTableLines, self._liloButtons])
      self._updateLiLoButtons()
      return pile
    elif self.cfg.cur_bootloader == 'grub2':
      comboBox = self._createComboBox(_("Install Grub2 files on:"), self.cfg.partitions)
      urwidm.connect_signal(comboBox, 'change', self._onGrub2FilesChange)
      urwidm.connect_signal(comboBox, 'focusgain', self._onHelpFocusGain, 'partition')
      urwidm.connect_signal(comboBox, 'focuslost', self._onHelpFocusLost)
      self._grub2BtnEdit = self._createButton(_("_Edit configuration").replace("_", ""), on_press = self._editGrub2Conf)
      urwidm.connect_signal(self._grub2BtnEdit, 'focusgain', self._onHelpFocusGain, 'grub2edit')
      urwidm.connect_signal(self._grub2BtnEdit, 'focuslost', self._onHelpFocusLost)
      pile = urwidm.PileMore([comboBox, self._createCenterButtonsWidget([self._grub2BtnEdit])])
      self._onGrub2FilesChange(comboBox, comboBox.selected_item[0], None)
      return pile
    else:
      return urwidm.Text("")

  def _changeBootloaderSection(self):
    self._bootloaderSection.original_widget = self._createBootloaderSectionView()

  def _handleKeys(self, key):
    if not isinstance(key, tuple): # only keyboard input
      key = key.lower()
      if self._mode == 'main':
        if key in ('h', 'f2'):
          self._switchToContextualHelp()
        elif key in ('a', 'ctrl a'):
          self._switchToAbout()
        if key in ('q', 'f10'):
          self.main_quit()
      elif self._mode == 'help':
        if key in ('q', 'esc', 'enter'):
          self._mode = 'main'
          self._loop.widget = self._mainView
      elif self._mode == 'about':
        if key in ('q', 'esc', 'enter'):
          self._mode = 'main'
          self._loop.widget = self._mainView

  def _switchToContextualHelp(self):
    self._mode = 'help'
    if self._helpCtx == '':
      txt = _(u"<b>BootSetup will install a new bootloader on your computer.</b> \n\
\n\
A bootloader is required to load the main operating system of a computer and will initially display \
a boot menu if several operating systems are available on the same computer.").replace("<b>", "").replace("</b>", "")
    elif self._helpCtx == 'type':
      txt = _(u"Here you can choose between LiLo or Grub2 bootloader.\n\
Both will boot your Linux and eventually Windows.\n\
LiLo is the old way but still works pretty good. A good choice if you have a simple setup.\n\
Grub2 is a full-featured bootloader more robust (does not rely on blocklists).")
    elif self._helpCtx == 'mbr':
      txt = _(u"Select the device that will contain your bootloader.\n\
This is commonly the device you set your Bios to boot on.")
    elif self._helpCtx == 'lilotable':
      txt = _(u"Here you must define a boot menu label for each \
of the operating systems that will be displayed in your bootloader menu.\n\
Any partition for which you do not set a boot menu label will not be configured and will \
not be displayed in the bootloader menu.\n\
If several kernels are available within one partition, the label you have chosen for that \
partition will be appended numerically to create multiple menu entries for each of these kernels.\n\
Any of these settings can be edited manually in the configuration file.")
    elif self._helpCtx == 'liloup':
      txt = _(u"Use this arrow if you want to move the \
selected Operating System up to a higher rank.\n\
The partition with the highest rank will be displayed on the first line of the bootloader menu.\n\
Any of these settings can be edited manually in the configuration file.")
    elif self._helpCtx == 'lilodown':
      txt = _(u"Use this arrow if you want to move the \
selected Operating System down to a lower rank.\n\
The partition with the lowest rank will be displayed on the last line of the bootloader menu.\n\
Any of these settings can be edited manually in the configuration file.")
    elif self._helpCtx == 'liloedit':
      txt = _(u"Experienced users can \
manually edit the LiLo configuration file.\n\
Please do not tamper with this file unless you know what you are doing and you have \
read its commented instructions regarding chrooted paths.")
    elif self._helpCtx == 'lilocancel':
      txt = _(u"This will undo all settings (even manual modifications).")
    elif self._helpCtx == 'partition':
      txt = _(u"Select the partition that will contain the Grub2 files.\n\
These will be in /boot/grub/. This partition should be readable by Grub2.\n\
It is recommanded to use your / partition, or your /boot partition if you have one.")
    elif self._helpCtx == 'grub2edit':
      txt = _(u"You can edit the etc/default/grub file for \
adjusting the Grub2 settings.\n\
This will not let you choose the label or the order of the menu entries, \
it's automatically done by Grub2.")
    elif self._helpCtx == 'install':
      txt = _(u"Once you have defined your settings, \
click on this button to install your bootloader.")
    self._helpView.body._original_widget.widget_list[1].set_text(('strong', txt))
    self._loop.widget = self._helpView

  def _switchToAbout(self):
    self._mode = 'about'
    self._loop.widget = self._aboutView

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

  def _isDeviceValid(self, device):
    return not device.startswith(u"/") and os.path.exists(os.path.join(u"/dev", device))

  def _onMBRChange(self, combo, disk, pos):
    if self._isDeviceValid(disk):
      self.cfg.cur_mbr_device = disk
      return True
    else:
      return False

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
      self._errorDialog(_("\nAn Operating System label should not contain spaces.\n\nPlease verify and correct.\n"))
      editLabel.sensitive_attr = ('error', 'focus_error')
      return True
    elif errorType == 'max':
      self._errorDialog(_("\nAn Operating System label should not hold more than {max} characters.\n\nPlease verify and correct.\n".format(max = self._liloMaxChars)))
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
      self._errorDialog(_("Sorry, BootSetup is unable to find a Linux filesystem on your choosen boot entries, so cannot install LiLo.\n"))

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
        self._custom_lilo = False
        self._errorDialog(_("Sorry, BootSetup is unable to find a suitable text editor in your system. You will not be able to manually modify the LiLo configuration.\n"))
    self._updateLiLoButtons()

  def _cancelLiLoConf(self, button):
    lilocfg = self._lilo.getConfigurationPath()
    if os.path.exists(lilocfg):
      os.remove(lilocfg)
    self._custom_lilo = False
    self._updateLiLoButtons()
 
  def _set_sensitive_rec(self, w, state):
    w.sensitive = state
    if hasattr(w, "widget_list"):
      for w2 in w.widget_list:
        self._set_sensitive_rec(w2, state)
    elif hasattr(w, "cells"):
      for w2 in w.cells:
        self._set_sensitive_rec(w2, state)
  def _updateLiLoButtons(self):
    self._set_sensitive_rec(self._liloTable, not self._custom_lilo)
    self._liloTableLines.sensitive = not self._custom_lilo
    self._updateScreen()

  def _onGrub2FilesChange(self, combo, partition, pos):
    if self._isDeviceValid(partition):
      self.cfg.cur_boot_partition = partition
      self._updateGrub2EditButton()
      return True
    else:
      self._updateGrub2EditButton(False)
      return False

  def _updateGrub2EditButton(self, doTest = True):
    if doTest:
      partition = os.path.join(u"/dev", self.cfg.cur_boot_partition)
      if sltl.isMounted(partition):
        mp = sltl.getMountPoint(partition)
        doumount = False
      else:
        mp = sltl.mountDevice(partition)
        doumount = True
      self._grub2_conf = os.path.exists(os.path.join(mp, u"etc/default/grub"))
      if doumount:
        sltl.umountDevice(mp)
    else:
      self._grub2_conf = False
    self._grub2BtnEdit.sensitive = self._grub2_conf
    self._updateScreen()
  
  def _editGrub2Conf(self, button):
    partition = os.path.join(u"/dev", self.cfg.cur_boot_partition)
    if sltl.isMounted(partition):
      mp = sltl.getMountPoint(partition)
      doumount = False
    else:
      mp = sltl.mountDevice(partition)
      doumount = True
    grub2cfg = os.path.join(mp, u"etc/default/grub")
    launched = False
    for editor in ('vim', 'nano'):
      try:
        sltl.execCall([editor, grub2cfg], shell=False, env=None)
        launched = True
        break
      except:
        pass
    if not launched:
      self._errorDialog(_("Sorry, BootSetup is unable to find a suitable text editor in your system. You will not be able to manually modify the Grub2 default configuration.\n"))
    if doumount:
      sltl.umountDevice(mp)

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
    self._infoDialog(msg)
    self.main_quit()

  def main_quit(self):
    if self._lilo:
      del self._lilo
    if self._grub2:
      del self._grub2
    print "Bye _o/"
    raise urwidm.ExitMainLoop()
