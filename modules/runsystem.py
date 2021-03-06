import subprocess
import imp
import random
import string
import os
from datetime import datetime
from gluon.shell import exec_environment

def generateBuildId(length):
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))

def rate_limit_exeeded(environment, userId, maxConcurrentBuilds):
	db = environment.db

	query = db((db.current_builds.user == userId) & (db.current_builds.finished==False)).count()

	return query > maxConcurrentBuilds


def invokeBuild(mode, buildId, main, userId, language='Python', project=None, course=None):

	env = exec_environment('applications/PythonCheck/models/db.py')
	config = exec_environment('applications/PythonCheck/models/config.py')

	if config.RATE_LIMIT_ENABLED and rate_limit_exeeded(env, userId=userId, maxConcurrentBuilds=1):
		raise StandardError('Rate Limit Exeeded!')

	# import the build system
	buildModulePath = config.APPLICATION_PATH + '/modules/build/'
	build = imp.load_source('buildsystem.module', buildModulePath + language.lower() + '.py')

	ass = ''
	extendedBuildArgs = ''

	if env.EXERCISE_CONTAINS_SINGLE_FILE:
		main = env.EXERCISE_MAIN_FILE

	# check if we are developing for an exercise or just so
	if (project != None) & (course != None) & (mode=='submit'):	

		# check if exercise exists
		enrollment = env.db((env.db.enrollment.student==userId) & (env.db.enrollment.course==course)).select().first()
		if not(enrollment):
			raise StandardError('Exercise does not exist')

		# check if the date is valid
		course_exercise = env.db((env.db.course_exercise.exercise == project) & (env.db.course_exercise.course == course)).select().first()
		if (course_exercise.start_date > datetime.now()) or (course_exercise.end_date < datetime.now()):
			raise StandardError('Start or Enddate dont match')

		# check if the exercise was graded before
		if len(env.db((env.db.grading.enrollment==enrollment.id) & (env.db.grading.exercise==course_exercise.id)).select()) != 0:
			raise StandardError('Exercise was graded before')

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

	fileQuery = (env.db.files.project == project) & (env.db.files.course == course)

	for codeFile in env.db(fileQuery).select():
		# write src code into file
		file=None
		
		if codeFile.filename == main:
			file = open(filePath + build.mainFile(), 'w')
			codeFile.content = (codeFile.content or '') + '\r\n' + ass
		else:
			file = open(filePath + '/' + codeFile.filename, 'w')
		file.write(codeFile.content or '')
		file.close()

	# lock files
	if mode == 'submit':
		env.db(fileQuery).update(writeable=False)

	buildArgs = buildId + ' ' + filePath + ' ' + buildModulePath + ' ' + language.lower() + ' ' + mode + ' ' + extendedBuildArgs

	# write into database before creating the jail
	env.db.current_builds.insert(PID=None, BuildId=buildId, start_time=datetime.today(), user=userId)
	env.db.commit()

	p = subprocess.Popen(['python', config.WEB2PY_BIN, '-S', 'PythonCheck', '-M', '-R', config.BUILD_SCRIPT, '-A', buildArgs])


