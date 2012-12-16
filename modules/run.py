import subprocess
import imp
import random
import string
import os
from gluon.shell import exec_environment

def generateBuildId(length):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def invokeBuild(mode, buildId, main, language='Python', project=None, course=None, userId=None):
	# import the build system
	buildModule = '/usr/share/web2py2/applications/PythonCheck/modules/build/' + language.lower() + '.py'
	build = imp.load_source('buildsystem.module', buildModule)
	
	env = exec_environment('applications/PythonCheck/models/db.py')
	config = exec_environment('applications/PythonCheck/models/config.py')

	ass = ''
	extendedBuildArgs = ''

	if env.EXERCISE_CONTAINS_SINGLE_FILE:
		main = env.EXERCISE_MAIN_FILE

	# check if we are developing for an exercise or just so
	if (project != None) & (course != None) & (mode=='submit'):	
		pointCode = []
		for pointSet in env.db((env.db.points.exercise == project)).select():
			assertionCode = []
			for assertion in env.db((env.db.assertion.points == pointSet.id)).select():
				assertionCode.append(build.buildAssertion(function_name=assertion.function_name, arguments=assertion.arguments, expected_result=assertion.expected_result))
				#print buildAssertion(function_name=assertion.function_name, arguments=assertion.arguments, expected_result=assertion.expected_result)

			pointCode.append(build.buildPointSet(id=pointSet.id, assertions=assertionCode))
		
		ass = build.buildTests(pointCode)

		extendedBuildArgs += str(course) + ' ' + str(project) + ' ' + str(userId)
	else:
		mode='run'


	filePath=config.SRC_DIR + buildId[:config.BUILD_ID_SHORT_LENGTH]

	# ensure that the dirs are there
	if not os.path.exists(filePath):
		os.makedirs(filePath)

	for codeFile in env.db((env.db.files.project == project) & (env.db.files.course == course)).select():
		print codeFile.filename
		# write src code into file
		file=None
		
		if codeFile.filename == main:
			file = open(filePath + config.USER_SCRIPT_PATH, 'w')
			codeFile.content += '\r\n' + ass
		else:
			file = open(filePath + '/' + codeFile.filename, 'w')
		file.write(codeFile.content or '')
		file.close()

	buildArgs = buildId + ' ' + filePath + ' ' + buildModule + ' ' + mode + ' ' + extendedBuildArgs

	p = subprocess.Popen(['python', config.WEB2PY_BIN, '-S', 'PythonCheck', '-M', '-R', config.BUILD_SCRIPT, '-A', buildArgs])


