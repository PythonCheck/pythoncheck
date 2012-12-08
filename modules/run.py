import subprocess
import imp
import random
import string
import os
from gluon.shell import exec_environment

SRC_DIR = "/res/scripts/"
WEB2PY_BIN = '/usr/share/web2py2/web2py.py'
BUILD_ID_LENGTH = 512
BUILD_ID_SHORT_LENGTH = 32
CLIENT_TIMEOUT = 1500
BUILD_SCRIPT = 'applications/PythonCheck/private/build.py'

def generateBuildId(length):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def invokeBuild(mode, buildId, main, language='Python', project=None, course=None):
	# import the build system
	buildModule = '/usr/share/web2py2/applications/PythonCheck/modules/build/' + language.lower() + '.py'
	build = imp.load_source('buildsystem.module', buildModule)
	
	env = exec_environment('applications/PythonCheck/models/db.py')

	print env.auth.user_id

	# check if we are developing for an exercise or just so
	if (project != None) & (course != None) & (mode=='submit'):
		# retrieve version number of the code
		# for codeFile in db((db.files.project==project) & (db.files.course==course)).select(db.files.ALL):
			# if row.version > highestRev:
			#	highestRev=row.version
		# print 'highestRev:', highestRev
		print 'submitting'
	else:
		print 'run only!'
		mode='run'

	filePath=SRC_DIR + buildId[:BUILD_ID_SHORT_LENGTH] + '/'

	# ensure that the dirs are there
	if not os.path.exists(filePath):
		os.makedirs(filePath)

	for codeFile in env.db((env.db.files.project==project) & (env.db.files.course==course)).select():
		# write src code into file
		file=None
		
		if codeFile.filename == main:
			file = open(filePath + 'script.py', 'w')
		else:
			file = open(filePath + codeFile.filename, 'w')
		file.write(codeFile.content)
		file.close()

	buildArgs = buildId + ' ' + filePath + ' ' + buildModule
	p = subprocess.Popen(['python', WEB2PY_BIN, '-S', 'PythonCheck', '-M', '-R', BUILD_SCRIPT, '-A', buildArgs])