#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Config class helps storing the configuration for the bootloader setup.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import sys
import os

class Config:
  """
  Configuration for BootSetup
  """
  def __init__(self, bootloader, is_test, use_test_data):
    self.is_test = is_test
    self.use_test_data = use_test_data
    self._get_current_config(bootloader)
  def _get_current_config(self, bootloader):
    print 'Gathering current configuration…',
    sys.stdout.flush()
    self.cur_bootloader = bootloader
    if self.is_test:
      self.is_live = True
    else:
      self.is_live = os.path.isfile('/mnt/salt/salt-version') and os.path.isfile('/mnt/salt/tmp/distro_infos')
    if self.use_test_data:
      self.cur_mbr_disk = ''
      self.cur_boot_partition = ''
      self.partitions = []
    else:
      print 'TODO: use parts of salix live tools to findout these informations'
      self.cur_mbr_disk = 'sda'
      self.cur_boot_partition = 'sda1'
      self.partitions = [
            ['sda5', 'ext2', 'Slackware', 'Salix'],
            ['sda1', 'ntfs', 'Windows' 'Vista']
          ]
    print ' Done'
    sys.stdout.flush()
