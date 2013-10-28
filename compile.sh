#!/bin/sh
cd $(dirname $0)
[ -d build ] && rm -r build
mkdir build
for p in data/po/*.po; do
  l=$(basename $p .po)
	echo "Compiling $l language"
	msgfmt $p -o build/$l.mo || exit 1
done
intltool-merge data/po/ -d -u data/bootsetup.desktop.in build/bootsetup.desktop || exit 1
cat <<'EOF' > build/bootsetup
#!/bin/sh
exec python /usr/share/bootsetup/bootsetup.py "$@"
EOF
