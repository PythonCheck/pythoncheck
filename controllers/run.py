# coding: utf8
import subprocess
import platform
import random
import string

from subprocess import PIPE
from gluon.serializers import json

## CONFIG
SRC_DIR = "/res/scripts/"
WEB2PY_BIN = '/usr/share/web2py2/web2py.py'
BUILD_ID_LENGTH = 512
CLIENT_TIMEOUT = 1500
BUILD_SCRIPT = 'applications/PythonCheck/private/build.py'

def submit():
	print "Hi. We will now run the test."

# user code is saved to database
# user code is run
# the output is caputured and replied
def run():
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

	# write src code into file
	file=open(SRC_DIR + "main.py", 'w')
	file.write(src)
	file.close()

	# generate build id
	buildId = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(BUILD_ID_LENGTH))

	# invoke build
	p = subprocess.Popen(['python', WEB2PY_BIN, '-S', 'PythonCheck', '-M', '-R', BUILD_SCRIPT, '-A', buildId])
	
	# notify the client that the build is in progress now
	return dict(mode=mode, buildId=buildId, timeout=CLIENT_TIMEOUT)

def result():
	data = db(db.current_builds.BuildId == request.vars.buildId).select().first()

	# if the data is not available throw an error
	if data == None:
		errorObject = {'message':'Build ID does not exist'}
		raise HTTP(422, json(errorObject))

	# if data is available and the build has finsihed return the outputs
	if data.finished:
		return dict(finished=data.finished, output=data.output, error=data.error)

	# if data is available and the build is still running tell the client to wait
	else:
		return dict(finished=data.finished, timeout=CLIENT_TIMEOUT)
