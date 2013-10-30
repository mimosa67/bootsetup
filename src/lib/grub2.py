#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Grub2 for BootSetup.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import tempfile
import shutil
import os

class Grub2:
  
  def __init__(self):
    pass

  def install(self, mbr_device, boot_partition):
    print "TODO install Grub2"
    # TODO mount boot_partition
    # TODO mount /boot in boot_partition
    # TODO copy the grub2 files to the boot_partition
    # TODO run grub-install
    # TODO bind /proc /sys and /dev into the boot partition
    # TODO run update-grub in the boot partition chrooted
    # TODO umount all
