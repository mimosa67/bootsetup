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
      ('footer', 'dark blue', 'light gray', 'bold'),
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
    self._loop = urwid.MainLoop(self._view, self._palette, unhandled_input = self._unhandled_input)
    self._loop.run()

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
| H: Help, A: About, Q: Quit            |
+=======================================+
    """
    txtTitle = urwid.Text("BootSetup curses, version {ver}".format(ver = self._version), align = "center")
    txtIntro = urwid.Text("Introduction text")
    txtFooter = urwid.Text("H: Help, A: About, Q: Quit")
    header = urwid.AttrMap(txtTitle, 'header')
    footer = urwid.AttrMap(txtFooter, 'footer')
    pile = urwid.Pile([txtIntro])
    body = urwid.Filler(pile)
    frame = urwid.Frame(body, header, footer)
    self._view = frame

  def _unhandled_input(self, key):
    if key in ('q', 'Q'):
      self.main_quit()

  def main_quit(self):
    if self.lilo:
      del self.lilo
    if self.grub2:
      del self.grub2
    print "Bye _o/"
    raise urwid.ExitMainLoop()
