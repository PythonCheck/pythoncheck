files=( /usr/lib64/python26.zip  /usr/lib64/python2.6 /usr/lib64/python2.6/plat-linux2 /usr/lib64/python2.6/lib-tk /usr/lib64/python2.6/lib-old /usr/lib64/python2.6/lib-dynload /usr/lib64/python2.6/site-packages /usr/lib/python2.6/site-packages /usr/lib64/libpython2.6.so.1.0 /lib64/libpthread.so.0 /lib64/libdl.so.2 /lib64/libutil.so.1 /lib64/libm.so.6  )

for index in ${files[@]} 
do
	file=$index
	if [[ -h $index  ]]
	then
		f=`readlink -f $index`
		echo $f
		file=$index" "$f
	fi
	cp --parents -r $file  /root/jail
	echo to /root/rail$index
done
cp --parent /usr/bin/python /root/jail
