#!/bin/bash

ROOT=$1

SRCDIR=$2

if [ "$ROOT" = "/" ]
then
	echo "Invalid argument"
	exit 1
fi

if [ "$SRCDIR" = "/" ]
then
	echo "Invalid argument"
	exit 1
fi

rm -rf $ROOT
rm -rf $SRCDIR