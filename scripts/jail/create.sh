#!/bin/bash

# where the new root is created
ROOT=$1

# where the user sourcecode is located at the moment
SRCFILE=$2

# where the distroname_distroversion.list file is located to load the necessary files
DISTROFILE=$3

# get files
files=( $( < $DISTROFILE ) )

# create root
mkdir -p $ROOT

# copy any dynamically linked libraries or other necessary files
for index in ${files[@]} 
do
	file=$index
	if [[ -h $index  ]]
	then
		f=`readlink -f $index`
		file=$index" "$f
	fi
	cp --parents -r $file $ROOT
done

# copy binaries
cp --parent /usr/bin/python /bin/bash /bin/ls $ROOT

# copy src files
cp $SRCFILE $ROOT/script.py
