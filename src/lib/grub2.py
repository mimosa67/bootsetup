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
import codecs
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
      self.__debug(u"cleanning " + self._tmp)
      try:
        if os.path.exists(sltl.mounting._tempMountDir):
          self.__debug(u"Remove " + sltl.mounting._tempMountDir)
          os.rmdir(sltl.mounting._tempMountDir)
        self.__debug(u"Remove " + self._tmp)
        os.rmdir(self._tmp)
      except:
        pass

  def __debug(self, msg):
    if self.isTest:
      print u"Debug: " + msg
      with codecs.open("bootsetup.log", "a+", "utf-8") as fdebug:
        fdebug.write(u"Debug: {0}\n".format(msg))

  def _mountBootPartition(self, bootPartition):
    """
    Return the mount point
    """
    self.__debug(u"bootPartition = " + bootPartition)
    if sltl.isMounted(bootPartition):
      self.__debug(u"bootPartition already mounted")
      return sltl.getMountPoint(bootPartition)
    else:
      self.__debug(u"bootPartition not mounted")
      return sltl.mountDevice(bootPartition)

  def _mountBootInBootPartition(self, mountPoint):
    # assume that if the mount_point is /, any /boot directory is already accessible/mounted
    if mountPoint != '/' and os.path.exists(os.path.join(mountPoint, 'etc/fstab')):
      self.__debug(u"mp != / and etc/fstab exists, will try to mount /boot by chrooting")
      try:
        self.__debug(u"grep -q /boot {mp}/etc/fstab && chroot {mp} /sbin/mount /boot".format(mp = mountPoint))
        if sltl.execCall(u"grep -q /boot {mp}/etc/fstab && chroot {mp} /sbin/mount /boot".format(mp = mount_point)):
          self.__debug(u"/boot mounted in " + mp)
          self._bootInBootMounted = True
      except:
        pass

  def _bindProcSysDev(self, mountPoint):
    """
    bind /proc /sys and /dev into the boot partition
    """
    if mountPoint != "/":
      self.__debug(u"mount point ≠ / so mount /dev, /proc and /sys in " + mountPoint)
      self._procInBootMounted = True
      sltl.execCall(u'mount -o bind /dev {mp}/dev'.format(mp = mountPoint))
      sltl.execCall(u'mount -o bind /proc {mp}/proc'.format(mp = mountPoint))
      sltl.execCall(u'mount -o bind /sys {mp}/sys'.format(mp = mountPoint))

  def _unbindProcSysDev(self, mountPoint):
    """
    unbind /proc /sys and /dev into the boot partition
    """
    if self._procInBootMounted:
      self.__debug(u"mount point ≠ / so umount /dev, /proc and /sys in " + mountPoint)
      sltl.execCall(u'umount {mp}/dev'.format(mp = mountPoint))
      sltl.execCall(u'umount {mp}/proc'.format(mp = mountPoint))
      sltl.execCall(u'umount {mp}/sys'.format(mp = mountPoint))

  def _copyAndInstallGrub2(self, mountPoint, device):
    if self.isTest:
      self.__debug(u"/usr/sbin/grub-install --boot-directory {bootdir} --no-floppy {dev}".format(bootdir = os.path.join(mountPoint, u"boot"), dev = device))
      return True
    else:
      return sltl.execCall(u"/usr/sbin/grub-install --boot-directory {bootdir} --no-floppy {dev}".format(bootdir = os.path.join(mountPoint, u"boot"), dev = device))

  def _installGrub2Config(self, mountPoint):
    if os.path.exists(os.path.join(mountPoint, u'etc/default/grub')) and os.path.exists(os.path.join(mountPoint, u'usr/sbin/update-grub')):
      self.__debug(u"grub2 package is installed on the target partition, so it will be used to generate the grub.cfg file")
      # assume everything is installed on the target partition, grub2 package included.
      if self.isTest:
        self.__debug(u"chroot {mp} /usr/sbin/update-grub".format(mp = mountPoint))
      else:
        sltl.execCall(u"chroot {mp} /usr/sbin/update-grub".format(mp = mountPoint))
    else:
      self.__debug(u"grub2 not installed on the target partition, so grub_mkconfig will directly be used to generate the grub.cfg file")
      # tiny OS installed on that mount point, so we cannot chroot on it to install grub2 config.
      if self.isTest:
        self.__debug(u"/usr/sbin/grub-mkconfig -o {cfg}".format(cfg = os.path.join(mountPoint, u"boot/grub/grub.cfg")))
      else:
        sltl.execCall(u"/usr/sbin/grub-mkconfig -o {cfg}".format(cfg = os.path.join(mountpoint, u"boot/grub/grub.cfg")))

  def _umountAll(self, mountPoint):
    self.__debug("umountAll")
    if mountPoint:
      self.__debug(u"umounting main mount point " + mountPoint)
      self._unbindProcSysDev(mountPoint)
      if self._bootInBootMounted:
        self.__debut(u"/boot mounted in " + mountPoint + u", so umount it")
        sltl.execCall(u"chroot {mp} /sbin/umount /boot".format(mp = mountPoint))
      if mountPoint != '/':
        self.__debug(u"umain mount point ≠ '/' → umount " + mountPoint)
        sltl.umountDevice(mountPoint)
    self._bootInBootMounted = False
    self._procInBootMounted = False

  def install(self, mbrDevice, bootPartition):
    mbrDevice = os.path.join("/dev", mbrDevice)
    bootPartition = os.path.join("/dev", bootPartition)
    self.__debug(u"mbrDevice = " + mbrDevice)
    self.__debug(u"bootPartition = " + bootPartition)
    self._bootInBootMounted = False
    self._procInBootMounted = False
    mp = None
    try:
      mp = self._mountBootPartition(bootPartition)
      self.__debug(u"mp = " + unicode(mp))
      self._mountBootInBootPartition(mp)
      if self._copyAndInstallGrub2(mp, mbrDevice):
        self._installGrub2Config(mp)
      else:
        sys.stderr.write(u"Grub2 cannot be installed on this disk [{0}]\n".format(mbrDevice))
    finally:
      self._umountAll(mp)
