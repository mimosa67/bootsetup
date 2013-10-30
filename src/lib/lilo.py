#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
LiLo for BootSetup.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import tempfile
import shutil
import os

class Lilo:
  
  def __init__(self):
    self._prefix = "bootsetup.lilo-"
    self._tmp = tempfile.mkdtemp(self._prefix)
    pass

  def __del__(self):
    print "nettoyage lilo"
    if self._tmp and os.path.exists(self._tmp):
      shutil.rmtree(self._tmp)

  def getConfigurationPath(self):
    return os.path.join(self._tmp, "lilo.conf")

  def createConfiguration(self, mbr_device, boot_partition, partitions):
    """
    paritions format: [device, filesystem, boot type, label]
    """
    self.mbr_device = mbr_device
    self.boot_partition = boot_partition
    self.partitions = partitions
    # TODO mount boot_partition
    # TODO mount /boot in boot_partition
    # TODO mount other partitions
    # TODO identify kernel+initrd in each linux partition
    # TODO umount all
    # TODO identify framebuffer type
    # TODO write configuration
    f = open(self.getConfigurationPath(), "w")
    f.write("""# LILO Configuration file
#TODO
""")
    f.close()

  def install(self):
    """
    Assuming that last configuration editing didn't modified mount point.
    """
    print "TODO install LiLo"
    # TODO mount boot_partition
    # TODO mount /boot in boot_partition
    # TODO bind /dev in boot_partition
    # TODO mount other partitions
    # TODO copy the configuration to the boot_partition
    # TODO run lilo
    # TODO umount all
