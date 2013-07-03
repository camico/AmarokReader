#!/bin/sh
TMPDIR=/tmp/AmarokReader
TARGET=/tmp/AmarokReader.amarokscript.tar.gz

rm -rfv $TMPDIR $TARGET
mkdir $TMPDIR
cp -rv . $TMPDIR
cd $TMPDIR
rm -rfv .idea/ *~ conTEXT/*pyc conTEXT/lib/*pyc conTEXT/filetypes/*pyc conTEXT/filetypes/legacy/*pyc conTEXT/.data conTEXT/.*py~
cd ..
tar czvf $TARGET AmarokReader/

echo
echo ...packaged to $TARGET
echo
echo is DEBUG turned off?
