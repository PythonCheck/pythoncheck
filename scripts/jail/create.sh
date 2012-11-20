ROOT=$1
SRCFILE=$2

files=( /lib64/libtinfo.so.5 /lib64/libdl.so.2 /lib64/librt.so.1 /lib64/libcap.so.2 /lib64/libacl.so.1 /lib64/libc.so.6 
	/lib64/libdl.so.2 /lib64/ld-linux-x86-64.so.2 /usr/lib64/python26.zip /usr/lib64/python2.6 /usr/lib64/python2.6/plat-linux2 
	/usr/lib64/python2.6/lib-tk /usr/lib64/python2.6/lib-old /usr/lib64/python2.6/lib-dynload /usr/lib64/python2.6/site-packages 
	/usr/lib/python2.6/site-packages /usr/lib64/libpython2.6.so.1.0 /lib64/libpthread.so.0 /lib64/libdl.so.2 /lib64/libutil.so.1 /lib64/libm.so.6 
)

# create 
mkdir -p $ROOT $ROOT

# copy any dynamically linked libraries
for index in ${files[@]} 
do
	file=$index
	if [[ -h $index  ]]
	then
		f=`readlink -f $index`
		echo $f
		file=$index" "$f
	fi
	cp --parents -r $file $ROOT
done

# copy binaries
cp --parent /usr/bin/python /bin/bash /bin/ls $ROOT

# copy src files
cp $SRCFILE $ROOT/script.py
 
# finally switch to root
chroot $ROOT
echo "DONE!"
