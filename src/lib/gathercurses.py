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
  
  # Other potential color schemes can be found at:
  # http://excess.org/urwid/wiki/RecommendedPalette
  _palette = [
      ('body', 'default', 'default'),
      ('focus', 'black', 'light gray'),
      ('header', 'light blue', 'default'),
      ('important', 'light red', 'default'),
      ('connected', 'dark green', 'default'),
      ('connected focus', 'black', 'dark green'),
      ('editcp', 'default', 'default', 'standout'),
      ('editbx', 'light gray', 'dark blue'),
      ('editfc', 'white', 'dark blue', 'bold'),
      ('editnfc', 'brown', 'default', 'bold'),
      ('tab active', 'dark green', 'light gray'),
      ('infobar', 'light gray', 'dark blue'),
      ('listbar', 'light blue', 'default'),
      # Simple colors around text
      ('green', 'dark green', 'default'),
      ('blue', 'light blue', 'default'),
      ('red', 'dark red', 'default'),
      ('bold', 'white', 'black', 'bold')
    ]
  _loop = None
  _view = None

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
    txt = urwid.Text("BootSetup curses version - Wip…")
    frame = urwid.Frame(urwid.AttrWrap(urwid.ListBox([txt]), 'plain'))
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
