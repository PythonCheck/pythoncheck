#!/bin/bash

ROOT=$1

if [ "$ROOT" = "/" ]
then
	echo "Invalid argument"
	exit 1
fi

rm -rf $ROOT