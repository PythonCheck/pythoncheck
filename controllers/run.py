# coding: utf8
import subprocess
import platform

from subprocess import PIPE

def submit():
	print "Hi. We will now run the test."

# user code is saved to database
# user code is run
# the output is caputured and replied
def run():
	# CONFIG
	JAIL_DIR = "/tmp/jail" 
	SRC_DIR = "/res/scripts/"
	DISTOLIST_PATH = "/usr/share/web2py2/applications/PythonCheck/scripts/jail/"
	SCRIPT_FILE = DISTOLIST_PATH + "create.sh"
	USER_SCRIPT_PATH = "/script.py"

	src=request.vars.code;
	language=request.vars.language
	exercise=request.vars.exercise
	course=request.vars.course
	mode=None

	# check if we are developing for an exercise or just so
	if (language != None) & (exercise != None) & (course != None):

		highestRev=0

		# (db.code.language==language) & (db.code.exercise==exercise) & (db.code.course==course)
		for row in db((db.code.language==language) & (db.code.exercise==exercise) & (db.code.course==course)).select(db.code.version):
			if row.version > highestRev:
				highestRev=row.version
		print 'highestRev:', highestRev

		mode='submit'
		#db.code.insert()
	else:
		print 'test only!'
		mode='test'

	## run code

	# write src code into file
	file=open(SRC_DIR + "main.py", 'w')
	file.write(src)
	file.close()

	# determine distro and therefore distro's .list file
	listfile = DISTOLIST_PATH + platform.dist()[0].lower() + "_" + platform.dist()[1].lower() + '.list'
	print listfile

	# create jail and copy src code into jail
	subprocess.call([SCRIPT_FILE, JAIL_DIR, SRC_DIR + "main.py", listfile]);

	# enter jail
	p = subprocess.Popen(["chroot", JAIL_DIR, "python", USER_SCRIPT_PATH], stdout=PIPE, stderr=PIPE)
	#TODO register in global process table for scheduler

	# wait for output
	p.wait()

	
	# capture output and prepare for printing
	output = p.stdout.read()
	error = p.stderr.read()

	return dict(output=output, error=error, mode=mode)
