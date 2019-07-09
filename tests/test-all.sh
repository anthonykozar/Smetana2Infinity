#!/bin/sh

for f in *.s2i ; do
	echo "../Smetana2Infinity.py $f"
	../Smetana2Infinity.py -u "$f"
	echo
done
