#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
Grub2 for BootSetup.
"""
__copyright__ = 'Copyright 2013-2014, Salix OS'
__license__ = 'GPL2+'

import tempfile
import os
import sys
import salix_livetools_library as sltl

class Grub2:
  
  isTest = False
  _prefix = None
  _tmp = None
  _bootInBootMounted = False
  _procInBootMounted = False
  
  def __init__(self, isTest):
    self.isTest = isTest
    self._prefix = "bootsetup.grub2-"
    self._tmp = tempfile.mkdtemp(prefix = self._prefix)
    sltl.mounting._tempMountDir = os.path.join(self._tmp, 'mounts')
    self.__debug("tmp dir = " + self._tmp)

  def __del__(self):
    if self._tmp and os.path.exists(self._tmp):
      self.__debug("cleanning " + self._tmp)
      try:
        if os.path.exists(sltl.mounting._tempMountDir):
          self.__debug("Remove " + sltl.mounting._tempMountDir)
          os.rmdir(sltl.mounting._tempMountDir)
        self.__debug("Remove " + self._tmp)
        os.rmdir(self._tmp)
      except:
        pass

  def __debug(self, msg):
    if self.isTest:
      print "Debug: " + msg

  def _mountBootPartition(self, bootPartition):
    """
    Return the mount point
    """
    self.__debug("bootPartition = " + bootPartition)
    if sltl.isMounted(bootPartition):
      self.__debug("bootPartition already mounted")
      return sltl.getMountPoint(bootPartition)
    else:
      self.__debug("bootPartition not mounted")
      return sltl.mountDevice(bootPartition)

  def _mountBootInBootPartition(self, mountPoint):
    # assume that if the mount_point is /, any /boot directory is already accessible/mounted
    if mountPoint != '/' and os.path.exists(os.path.join(mountPoint, 'etc/fstab')):
      self.__debug("mp != / and etc/fstab exists, will try to mount /boot by chrooting")
      try:
        self.__debug("grep -q /boot {mp}/etc/fstab && chroot {mp} /sbin/mount /boot".format(mp = mountPoint))
        if sltl.execCall("grep -q /boot {mp}/etc/fstab && chroot {mp} /sbin/mount /boot".format(mp = mount_point)):
          self.__debug("/boot mounted in " + mp)
          self._bootInBootMounted = True
      except:
        pass

  def _bindProcSysDev(self, mountPoint):
    """
    bind /proc /sys and /dev into the boot partition
    """
    if mountPoint != "/":
      self.__debug("mount point ≠ / so mount /dev, /proc and /sys in " + mountPoint)
      self._procInBootMounted = True
      sltl.execCall('mount -o bind /dev {mp}/dev'.format(mp = mountPoint))
      sltl.execCall('mount -o bind /proc {mp}/proc'.format(mp = mountPoint))
      sltl.execCall('mount -o bind /sys {mp}/sys'.format(mp = mountPoint))

  def _unbindProcSysDev(self, mountPoint):
    """
    unbind /proc /sys and /dev into the boot partition
    """
    if self._procInBootMounted:
      self.__debug("mount point ≠ / so umount /dev, /proc and /sys in " + mountPoint)
      sltl.execCall('umount {mp}/dev'.format(mp = mountPoint))
      sltl.execCall('umount {mp}/proc'.format(mp = mountPoint))
      sltl.execCall('umount {mp}/sys'.format(mp = mountPoint))

  def _copyAndInstallGrub2(self, mountPoint, device):
    if self.isTest:
      self.__debug("/usr/sbin/grub-install --boot-directory {bootdir} --no-floppy {dev}".format(bootdir = os.path.join(mountPoint, "boot"), dev = device))
      return True
    else:
      return sltl.execCall("/usr/sbin/grub-install --boot-directory {bootdir} --no-floppy {dev}".format(bootdir = os.path.join(mountPoint, "boot"), dev = device))

  def _installGrub2Config(self, mountPoint):
    if os.path.exists(os.path.join(mountPoint, 'etc/default/grub')) and os.path.exists(os.path.join(mountPoint, 'usr/sbin/update-grub')):
      self.__debug("grub2 package is installed on the target partition, so it will be used to generate the grub.cfg file")
      # assume everything is installed on the target partition, grub2 package included.
      if self.isTest:
        self.__debug("chroot {mp} /usr/sbin/update-grub".format(mp = mountPoint))
      else:
        sltl.execCall("chroot {mp} /usr/sbin/update-grub".format(mp = mountPoint))
    else:
      self.__debug("grub2 not installed on the target partition, so grub_mkconfig will directly be used to generate the grub.cfg file")
      # tiny OS installed on that mount point, so we cannot chroot on it to install grub2 config.
      if self.isTest:
        self.__debug("/usr/sbin/grub-mkconfig -o {cfg}".format(cfg = os.path.join(mountPoint, "boot/grub/grub.cfg")))
      else:
        sltl.execCall("/usr/sbin/grub-mkconfig -o {cfg}".format(cfg = os.path.join(mountpoint, "boot/grub/grub.cfg")))

  def _umountAll(self, mountPoint):
    self.__debug("umountAll")
    if mountPoint:
      self.__debug("umounting main mount point " + mountPoint)
      self._unbindProcSysDev(mountPoint)
      if self._bootInBootMounted:
        self.__debut("/boot mounted in " + mountPoint + ", so umount it")
        sltl.execCall("chroot {mp} /sbin/umount /boot".format(mp = mountPoint))
      if mountPoint != '/':
        self.__debug("main mount point ≠ '/' → umount " + mountPoint)
        sltl.umountDevice(mountPoint)
    self._bootInBootMounted = False
    self._procInBootMounted = False

  def install(self, mbrDevice, bootPartition):
    mbrDevice = os.path.join("/dev", mbrDevice)
    bootPartition = os.path.join("/dev", bootPartition)
    self.__debug("mbrDevice = " + mbrDevice)
    self.__debug("bootPartition = " + bootPartition)
    self._bootInBootMounted = False
    self._procInBootMounted = False
    mp = None
    try:
      mp = self._mountBootPartition(bootPartition)
      self.__debug("mp = " + unicode(mp))
      self._mountBootInBootPartition(mp)
      if self._copyAndInstallGrub2(mp, mbrDevice):
        self._installGrub2Config(mp)
      else:
        sys.stderr.write("Grub2 cannot be installed on this disk [{0}]\n".format(mbrDevice))
    finally:
      self._umountAll(mp)
