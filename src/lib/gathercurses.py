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
import urwid
import re
import math
import subprocess
from common import *
from config import *
import salix_livetools_library as sltl
import urwid_wicd.curses_misc as urwicd
from lilo import *
from grub2 import *

class GatherCurses:
  """
  UI in curses/urwid to gather information about the configuration to setup.
  """
  
  _version = 0.1
  # Other potential color schemes can be found at:
  # http://excess.org/urwid/wiki/RecommendedPalette
  _palette = [
      ('body', 'default', 'default'),
      ('header', 'dark red', 'light gray', 'bold'),
      ('footer', 'light green', 'dark gray', 'bold'),
      ('footer_key', 'yellow', 'black', 'bold'),
    ]
  _view = None
  _loop = None

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
    self.lilo = self.grub2 = None
  
  def run(self):
    urwid.set_encoding('utf8')
    ui = urwid.raw_display.Screen()
    ui.set_mouse_tracking()
    self._createView()
    self._loop = urwid.MainLoop(self._view, self._palette, handle_mouse = True, unhandled_input = self._handleKeys)
    self._loop.run()

  def _createCenterButtonsWidget(self, buttons, h_sep = 0, v_sep = 0):
    maxLen = 0
    for button in buttons:
      maxLen = max(maxLen, len(button.get_label()))
    return urwid.GridFlow(buttons, cell_width = maxLen + len('<  >'), h_sep = h_sep, v_sep = v_sep, align = "center")

  def _createView(self):
    """
+=======================================+
|                 Title                 |
+=======================================+
| Introduction text                     |
+---------------------------------------+
| Bootloader: (×) LiLo (_) Grub2        |
| MBR Device:  |____________vvv|        | <== ComboBox thanks to wicd
| Grub2 files: |____________vvv|        | <== Grub2 only
| +-----------------------------------+ | --+
| |Dev.|FS  |Type |Label      |Actions| |   |
| |sda1|ext4|Salix|Salix14____|<↑><↓> | |   |
| |sda5|xfs |Arch |ArchLinux__|<↑><↓> | |   +- <== LiLo only
| +-----------------------------------+ |   |
| <Edit config>                         |   |
| <Undo custom config>                  | --+
| <Install>                             |
+=======================================+
| H: Help, A: About, Q: Quit            | <== Action keyboard thanks to wicd
+=======================================+
    """
    txtTitle = urwid.Text(_("BootSetup curses, version {ver}").format(ver = self._version), align = "center")
    header = urwid.AttrMap(txtTitle, 'header')
    keys = [
        ('H', " " + _("Help")),
        ('A', " " + _("About")),
        ('Q', " " + _("Quit"))
      ]
    keysColumns = urwicd.OptCols(keys, self._handleKeys, attrs = ('footer_key', 'footer'))
    footer = urwid.AttrMap(keysColumns, 'footer')
    txtIntro = urwid.Text(_("Introduction text"))
    
    lblBootloader = urwid.Text(_("Bootloader:"))
    radioGroupBootloader = []
    radioLiLo = urwid.RadioButton(radioGroupBootloader, "LiLo", on_state_change = self._onLiLoChange)
    radioGrub2 = urwid.RadioButton(radioGroupBootloader, "Grub2", on_state_change = self._onGrub2Change)
    bootloaderTypeSection = urwid.Columns([lblBootloader, radioLiLo, radioGrub2], focus_column = 1)

    mbrDeviceSection =self._createMbrDeviceSectionView()

    bootloaderSection = self._createBootloaderSectionView()

    btnInstall = urwid.Button(_("Install"), on_press = self._onInstall)
    installSection = self._createCenterButtonsWidget([btnInstall])

    bodyList = [txtIntro, urwid.Divider('─'), bootloaderTypeSection, mbrDeviceSection, bootloaderSection, urwid.Divider('─'), installSection]

    body = urwid.AttrWrap(urwid.ListBox(urwid.SimpleListWalker(bodyList)), 'body')
    frame = urwid.Frame(body, header, footer, focus_part = 'body')
    self._view = frame

  def _createMbrDeviceSectionView(self):
    return urwid.WidgetPlaceholder(urwid.Text("mbr device section"))

  def _createBootloaderSectionView(self):
    return urwid.WidgetPlaceholder(urwid.Text("bootloader section"))

  def _handleKeys(self, key):
    if key in ('q', 'Q'):
      self.main_quit()

  def _onLiLoChange(self, radioLiLo, newState):
    pass

  def _onGrub2Change(self, radioGrub2, newState):
    pass

  def _onInstall(self, btnInstall):
    pass

  def main_quit(self):
    if self.lilo:
      del self.lilo
    if self.grub2:
      del self.grub2
    print "Bye _o/"
    raise urwid.ExitMainLoop()
