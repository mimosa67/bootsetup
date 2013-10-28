#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set et ai sta sw=2 ts=2 tw=0:
"""
BootSetup helps installing LiLo or Grub2 on your computer.
This is the launcher.
"""
__app__ = 'bootsetup'
__copyright__ = 'Copyright 2013-2014, Salix OS'
__author__ = 'Cyrille Pontvieux <jrd~at~enialis~dot~net> and Pierrick Le Brun <akuna~at~salixos~dot~org>'
__credits__ = ['Cyrille Pontvieux', 'Pierrick Le Brun']
__maintainer__ = 'Cyrille Pontvieux'
__email__ = 'jrd~at~enialis~dot~net'
__license__ = 'GPL2+'
__version__ = '0.1'

import os
import sys

def usage():
  print """BootSetup v{ver}
{copyright}
{license}
{author}

  bootsetup.py [--help] [--version] [--test [--data]]

Parameters:
  --help: Show this help message
  --version: Show the BootSetup version
  --test: Run it in test mode
    --data: Run it with some pre-filled data
""".format(ver = __version__, copyright = __copyright__, license = __license__, author = __author__)

if __name__ == '__main__':
  os.chdir(os.path.dirname(__file__))
  is_graphic = bool(os.environ.get('DISPLAY'))
  is_test = False
  use_test_data = False
  for arg in sys.argv[1:]: # argv[0] = own name
    if arg == '--help':
      usage()
      sys.exit(0)
    elif arg == '--version':
      print __version__
      sys.exit(0)
    elif arg == '--test':
      is_test = True
      print "*** Testing mode ***"
    elif is_test and arg == '--data':
      use_test_data = True
      print "*** Test data mode ***"
    else:
      sys.stderr.write("Unrecognized parameter '{0}'.\n".format(arg))
      sys.exit(1)
  locale_dir = '/usr/share/locale'
  if is_test:
    locale_dir = '../data/locale'
  print 'BootSetup v' + __version__
  if is_graphic:
    from lib.bootsetup_gtk import *
  else:
    from lib.bootsetup_curses import *
  run_setup(__app__, locale_dir, __version__, is_test, use_test_data)
