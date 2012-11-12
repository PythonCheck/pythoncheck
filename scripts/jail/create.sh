ROOT=/root/jail
INCPATH=/lib64/
includes=( "/lib64/libtinfo.so.5" /lib64/libdl.so.2 /lib64/librt.so.1 /lib64/libcap.so.2 /lib64/libacl.so.1 /lib64/libc.so.6 /lib64/libdl.so.2 /lib64/ld-linux-x86-64.so.2 )

mkdir -p $ROOT/lib64 $ROOT/bin
cp /bin/bash /bin/ls $ROOT/bin/

# copy any dynamically linked libraries
for inc in ${includes[@]}
do
	cp $inc $ROOT$INCPATH
	echo $inc
done
 
# finally switch to root
chroot $ROOT
echo "DONE!"
