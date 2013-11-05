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
import salix_livetools_library as sltl

class Grub2:
  
  isTest = False
  _prefix = None
  _tmp = None
  
  def __init__(self, isTest):
    self.isTest = isTest
    self._prefix = "bootsetup.grub2-"
    self._tmp = tempfile.mkdtemp(prefix = self._prefix)
    sltl.mounting._tempMountDir = os.path.join(self._tmp, 'mounts')
    if isTest:
      print "tmp dir = {0}".format(self._tmp)

  def __del__(self):
    print "nettoyage grub2"
    if self._tmp and os.path.exists(self._tmp):
      if self.isTest:
        print "rm -r " + self._tmp
      else:
        shutil.rmtree(self._tmp)

  def _mountBootPartition(self, boot_partition):
    """
    Return the mount point
    """
    if sltl.isMounted(boot_partition):
      return sltl.getMountPoint(boot_partition)
    else:
      return sltl.mountDevice(boot_partition)

  def _mountBootInBootPartition(self, mountPoint):
    # assume that if the mount_point is /, any /boot directory is already accessible/mounted
    if mount_point != '/' and os.path.exists(os.path.join(mount_point, 'etc/fstab')):
      try:
        if sltl.execCall("grep /boot {mp}/etc/fstab && chroot {mp} /sbin/mount /boot".format(mp = mount_point)):
          self._bootInBootMounted = True
      except:
        pass

  def _bindProcSysDev(self, mount_point):
    """
    bind /proc /sys and /dev into the boot partition
    """
    if mount_point != "/":
      self._procInBootMounted = True
      sltl.execCall('mount -o bind /dev {mp}/dev'.format(mp = mount_point))
      sltl.execCall('mount -o bind /proc {mp}/proc'.format(mp = mount_point))
      sltl.execCall('mount -o bind /sys {mp}/sys'.format(mp = mount_point))

  def _unbindProcSysDev(self, mount_point):
    """
    unbind /proc /sys and /dev into the boot partition
    """
    if self._procInBootMounted:
      sltl.execCall('umount {mp}/dev'.format(mp = mount_point))
      sltl.execCall('umount {mp}/proc'.format(mp = mount_point))
      sltl.execCall('umount {mp}/sys'.format(mp = mount_point))

  def _copyAndInstallGrub2(self, mount_point, device):
    if self.isTest:
      print "grub-install --boot-directory {bootdir} --no-floppy {dev}".format(bootdir = os.path.join(mount_point, "boot"), dev = device)
      return 0
    else:
      return sltl.execCall("grub-install --boot-directory {bootdir} --no-floppy {dev}".format(bootdir = os.path.join(mount_point, "boot"), dev = device))

  def _installGrub2Config(self, mount_point):
    if os.path.exists(os.path.join(mount_point, 'etc/default/grub')) and os.path.exists(os.path.join(mount_point, 'usr/sbin/update-grub')):
      # assume everything is installed on the target partition, grub2 package included.
      if self.isTest:
        print "chroot {mp} /usr/sbin/update-grub".format(mp = mount_point)
      else:
        sltl.execCall("chroot {mp} /usr/sbin/update-grub".format(mp = mount_point))
    else:
      # tiny OS installed on that mount point, so we cannot chroot on it to install grub2 config.
      if self.isTest:
        print "grub-mkconfig -o {cfg}".format(cfg = os.path.join(mount_point, "boot/grub/grub.cfg"))
      else:
        sltl.execCall("grub-mkconfig -o {cfg}".format(cfg = os.path.join(mount_point, "boot/grub/grub.cfg")))

  def _umountAll(self, mount_point):
    if mount_point:
      self._unbindProcSysDev(mount_point)
      if self._bootInBootMounted:
        sltl.execCall("chroot {mp} /sbin/umount /boot".format(mp = mount_point))
      if mount_point != '/':
        sltl.umountDevice(mount_point)

  def install(self, mbr_device, boot_partition):
    self._bootInBootMounted = False
    self._procInBootMounted = False
    mp = None
    try:
      mp = self._mountBootPartition(self.boot_partition)
      self._mountBootInBootPartition(mp)
      if self._copyAndInstallGrub2(mp, self.mbr_device):
        self._installGrub2Config(mp)
      else:
        sys.stderr.write("Grub2 cannot be installed on this disk [{0}]\n".format(self.mbr_device))
    finally:
      self._umountAll(mp)
    self._bootInBootMounted = False
    self._procInBootMounted = False
