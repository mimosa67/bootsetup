#!/bin/sh
cd $(dirname $0)
if [ ! -d build ]; then
  echo "Run compile.sh first" >&2
  exit 1
fi
if [ -z "$DESTDIR" ] || [ ! -d "$DESTDIR" ]; then
  echo "DESTDIR variable not set or directory does not exist" >&2
  exit 2
fi
VER=$(python -c "
import os
os.chdir('src')
from bootsetup import __version__
print __version__,
")
install -D -m 755 xsu $DESTDIR/usr/bin/xsu
install -D -m 755 build/bootsetup $DESTDIR/usr/sbin/bootsetup
install -D -m 644 build/bootsetup.desktop $DESTDIR/usr/share/applications/bootsetup.desktop
for size in 24 64 128; do
  install -D -m 644 data/icons/bootsetup-${size}.png $DESTDIR/usr/share/icons/hicolor/${size}x${size}/apps/bootsetup.png
done
install -D -m 644 data/icons/bootsetup.svg $DESTDIR/usr/share/icons/hicolor/scalable/apps/bootsetup.svg
for f in src/lib/*.py; do
  install -D -m 644 $f $DESTDIR/usr/share/bootsetup/lib/$(basename $f)
done
for f in src/resources/*; do
  install -D -m 644 $f $DESTDIR/usr/share/bootsetup/resources/$(basename $f)
done
install -D -m 755 src/bootsetup.py $DESTDIR/usr/share/bootsetupr/bootsetup.py
(
  cd $DESTDIR/usr/share/bootsetup
  echo "
import sys
from compiler import compileFile
for f in sys.argv[1:]:
  print '{0}c'.format(f)
  compileFile(f)
" | python -- - $(find . -type f -name '*.py')
)
for m in build/*.mo; do
  l=$(basename $m .mo)
	install -D -m 644 $m $DESTDIR/usr/share/locale/$l/LC_MESSAGES/bootsetup.mo
done
for f in docs/*; do
	install -D -m 644 $f $DESTDIR/usr/doc/bootsetup-$VER/$(basename $f)
done
