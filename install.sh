#!/bin/bash

# set defaults
WEB2PYURL='http://www.web2py.com/examples/static/web2py_src.zip'
PCURL='http://192.168.1.4/PythonCheck.zip'
DEFWEB2PYLOC='/usr/share/'
TEMPWEB2PYLOC='/tmp'
TEMPWEB2PYNAME='web2py.zip'
TEMPPCNAME='pythoncheck.zip'

echo 'Hi there. I will assist you in setting up PythonCheck.'
echo 'Please make sure you have an internet connection otherwise this could get a little bit complicated.'
echo  
echo 'I will ask you for some information to customize your installation. If you just hit enter, you will'
echo 'receive an default installation using the information provided between the [brackets]'

echo 'Up next: The web2py installation.'

echo -n 'Enter the path to your web2py installation [hit enter if you havent installed it allready] '
read WEB2PY

if [ "$WEB2PY" = "" ]
then
	
	echo
	echo 'Right. I will download the web2py plattform. Please tell me where you would like to install web2py to.'
	echo -n "web2py install location (/web2py will be added to the end of the path) [$DEFWEB2PYLOC] "
	read WEB2PYLOC


	if [ "$WEB2PYLOC" = "" ]
	then
		WEB2PYLOC=$DEFWEB2PYLOC
	fi

	mkdir -p "$TEMPWEB2PYLOC"

	if [ "$(which curl)" != "" ]
	then
		curl -L $WEB2PYURL -o $TEMPWEB2PYLOC'/'$TEMPWEB2PYNAME
	elif [ "$(which wget)" != "" ]
	then
		wget -O $TEMPWEB2PYLOC'/'$TEMPWEB2PYNAME $WEB2PYURL
	else
		echo 'Sorry, I found no tool to download web2py. I need either curl or wget. But I really need at least one of them :('
		exit 1
	fi


	if [ -e $TEMPWEB2PYLOC'/'$TEMPWEB2PYNAME ]
	then
		echo 'Cool. We have downloaded web2py successfully! I will now install web2py'
		mkdir -p "$WEB2PYLOC"

		unzip -d $WEB2PYLOC $TEMPWEB2PYLOC'/'$TEMPWEB2PYNAME
		WEB2PY=$WEB2PYLOC
		echo 'Whew. Done. At least with web2py. Now we will install the PythonCheck application'
		
	else
		echo 'Sorry. It seems like I failed to install web2py. Maybe try to install it by hand and tell me the location'
		exit 1
	fi
fi

echo 'Please tell me where the PythonCheck.zip is located so I can install it on you web2py instance'
PCPATH=''
while [ "$PCPATH" = "" ] || [ ! -e "$PCPATH" ]
do
	echo -n '/path/to/pythoncheck.zip [no default!] or "d" to download it '
	read PCPATH

	if [ "$PCPATH" = "exit" ]
	then
		echo 'Exiting on you command.'
		exit 1
	fi

	if [ "$PCPATH" = "d" ]
	then
		echo 'Ok, I will download the latest release'
		if [ "$(which curl)" != "" ]
		then
			curl -L $PCURL -o $TEMPWEB2PYLOC'/'$TEMPPCNAME
		elif [ "$(which wget)" != "" ]
		then
			wget -O $TEMPWEB2PYLOC'/'$TEMPPCNAME $PCURL
		else
			echo 'Sorry, I found no tool to download PythonCheck. I need either curl or wget. But I really need at least one of them :('
			exit 1
		fi

		PCPATH=$TEMPWEB2PYLOC'/'$TEMPPCNAME
	fi

	if [ "$PCPATH" = "" ] || [ ! -e "$PCPATH" ]
	then
		echo 'Nope. That wasnt the path. Try again. Or enter "exit" to exit'
	fi
done

unzip -d $WEB2PY'/applications' $TEMPWEB2PYLOC'/'$TEMPPCNAME || (echo 'Couldnt unzip the PythonCheck application.' && exit 1)

echo 'Awesome. It looks like we have successfully unzipped the PythonCheck application'
echo
echo ''





