#!/bin/sh
cd $(dirname "$0")
if [ -d data/po ] && [ $(find data/po -maxdepth 1 -name '*.po'|wc -l) -gt 0 ]; then
  for p in data/po/*.po; do
    d=$(basename $p .po)
    if [ ! -d data/locale/$d ]; then
      mkdir -p data/locale/$d/LC_MESSAGES
      echo "$p..."
      msgfmt $p -o data/locale/$d/LC_MESSAGES/bootsetup.mo
    fi
  done
fi
[ -e src/bootsetup.log ] && rm src/bootsetup.log
./src/bootsetup.py --test "$@"
