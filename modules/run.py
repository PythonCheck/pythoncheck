import subprocess
import imp
import random
import string
from gluon.shell import exec_environment

SRC_DIR = "/res/scripts/"
WEB2PY_BIN = '/usr/share/web2py2/web2py.py'
BUILD_ID_LENGTH = 512
BUILD_ID_SHORT_LENGTH = 32
CLIENT_TIMEOUT = 1500
BUILD_SCRIPT = 'applications/PythonCheck/private/build.py'

def generateBuildId(length):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def invokeBuild(code, mode, buildId, language='Python', exercise=None, course=None):
	# import the build system
	buildModule = '/usr/share/web2py2/applications/PythonCheck/modules/build/' + language.lower() + '.py'
	build = imp.load_source('buildsystem.module', buildModule)
	
	env = exec_environment('applications/PythonCheck/models/db.py')

	sourceCode=code

	print build.binary()

	print env.auth.user_id

	# check if we are developing for an exercise or just so
	if (language != None) & (exercise != None) & (course != None) & (mode=='submit'):

		highestRev=0

		# retrieve version number of the code
		for row in db((db.code.language==language) & (db.code.exercise==exercise) & (db.code.course==course)).select(db.code.version):
			if row.version > highestRev:
				highestRev=row.version
		print 'highestRev:', highestRev

	else:
		print 'run only!'
		mode='run'

	# write src code into file
	filePath=SRC_DIR + "main" + buildId[:BUILD_ID_SHORT_LENGTH] + ".py"
	file=open(filePath, 'w')
	file.write(sourceCode)
	file.close()

	buildArgs = buildId + ' ' + filePath + ' ' + buildModule
	p = subprocess.Popen(['python', WEB2PY_BIN, '-S', 'PythonCheck', '-M', '-R', BUILD_SCRIPT, '-A', buildArgs])