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

  def _mountBootPartition(self, boot_partition):
    """
    Return the mount point
    """
    # TODO mount boot_partition
    return ""

  def _mountBootInBootPartition(self, mount_point):
    # TODO mount /boot in boot_partition
    pass

  def _copyGrub2FilesIfNeeded(self, mount_point):
    # TODO copy the grub2 files to the boot_partition
    pass

  def _bindProcSysDev(self, mount_point):
    # TODO bind /proc /sys and /dev into the boot partition
    pass

  def _unbindProcSysDev(self, mount_point):
    # TODO unbind /proc /sys and /dev into the boot partition
    pass

  def _umountAll(self, mount_point, mountPointList):
    # TODO umount all
    pass

  def install(self, mbr_device, boot_partition):
    print "TODO install Grub2"
    mp = None
    try:
      mp = self._mountBootPartition(self.boot_partition)
      self._mountBootInBootPartition(mp)
      self._copyGrub2FilesIfNeeded(mp)
      # TODO run grub-install
      self._bindProcSysDev(mp)
      # TODO run update-grub in the boot partition chrooted
    finally:
      if mp:
        self._unbindProcSysDev(mp)
      self._umountAll()
