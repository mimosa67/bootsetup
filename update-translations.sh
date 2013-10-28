#!/bin/sh
cd $(dirname "$0")
# create data/po/bootsetup.pot template file from glade file
xgettext --from-code=utf-8 \
	-L Glade \
	-o data/po/bootsetup.pot \
	src/resources/bootsetup.glade
# update data/po/bootsetup.pot template file from python files
for p in src/lib/*.py; do
  xgettext --from-code=utf-8 \
    -j \
    -L Python \
    -o data/po/bootsetup.pot \
    $p
done
# create data/bootsetup.desktop.in.h containing the key to translate
intltool-extract --type="gettext/ini" data/bootsetup.desktop.in
# use the .in.h file to update the template file
xgettext --from-code=utf-8 \
  -j \
  -L C \
  -kN_ \
  -o data/po/bootsetup.pot \
  data/bootsetup.desktop.in.h
# remove unused .in.h file
rm data/bootsetup.desktop.in.h
# update the po files using the pot file
(
  cd data/po
  for p in *.po; do
	  msgmerge -U $p bootsetup.pot
  done
  rm -f ./*~
)
