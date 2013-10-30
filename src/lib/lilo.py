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
import salix_livetools_library as sltl

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

  def _mountBootPartition(self, boot_partition):
    """
    Return the mount point
    """
    # TODO mount boot_partition
    return ""

  def _mountBootInBootPartition(self, mount_point):
    # TODO mount /boot in boot_partition
    pass

  def _mountPartitions(self, partitions):
    """
    Return a list of mount points for each partition
    """
    # TODO mount other partitions
    return []

  def _createLiloSections(self, partitions, mountPointList):
    """
    Return a list of lilo section string for each partition.
    There could be more section than partitions if there are multiple kernels.
    """
    # TODO identify kernel+initrd in each linux partition
    return []

  def _umountAll(self, mount_point, mountPointList):
    # TODO umount all
    pass

  def _getFrameBufferConf(self):
    """
    Return the frame buffer configuration for this hardware.
    """
    # TODO identify framebuffer type
    return "normal"

  def createConfiguration(self, mbr_device, boot_partition, partitions):
    """
    paritions format: [device, filesystem, boot type, label]
    """
    self.mbr_device = mbr_device
    self.boot_partition = boot_partition
    self.partitions = partitions
    mp = self._mountBootPartition(boot_partition)
    self._mountBootInBootPartition(mp)
    mpList = self._mountPartitions(partitions)
    liloSections = self._createLiloSections(partitions, mpList)
    self._umountAll()
    fb = self._getFrameBufferConf()
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
    mp = self._mountBootPartition(boot_partition)
    self._mountBootInBootPartition(mp)
    # TODO bind /dev in boot_partition
    mpList = self._mountPartitions(partitions)
    # TODO copy the configuration to the boot_partition
    # TODO run lilo
    self._umountAll()
