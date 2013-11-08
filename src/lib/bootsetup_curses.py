#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Curses BootSetup.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import gettext
import os
from common import *
from gathercurses import *
import urwid

def run_setup(app_name, locale_dir, version, bootloader, target_partition, is_test, use_test_data):
  gettext.install(app_name, locale_dir, True)
  if not is_test and os.getuid() != 0:
    error_dialog(_("Root privileges are required to run this program."), _("Sorry!"))
    sys.exit(1)
  gc = GatherCurses(version, bootloader, target_partition, is_test, use_test_data)
  gc.run()
