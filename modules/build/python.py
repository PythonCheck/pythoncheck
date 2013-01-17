import platform
import subprocess
import os
import datetime
from subprocess import PIPE

GRADING_FILE = '/grades.grd'

# path where the distrolists are located
DISTOLIST_PATH = '$APP/scripts/jail/' 

# path of the create script that creates the jail
SCRIPT_FILE = DISTOLIST_PATH + 'create.sh'

# path of the cleanup script that cleans up a build
CLEANUP_FILE = DISTOLIST_PATH + 'cleanup.sh'

## JAIL SETTINGS 
# location of the main script in the jail 
USER_SCRIPT_PATH = '/script.py'

# create files

def buildFile(filename=None, contents=None):
	return '# -*- coding: utf-8 -*-\n' + (contents or '')

def lineComment(str):
	return '# ' + str

def blockComment(str):
	return '\n'.join([ ('# ' + line) for line in str.split('\n') ])

# build

def preBuild(db, buildId, sourceCodeFolder, env):
	# determine distro and therefore distro's .list file
	listfile = path(DISTOLIST_PATH, env) + platform.dist()[0].lower() + "_" + platform.dist()[1].lower() + '.list'

	# check if we found a valid listfile. if not generate an error and stop building
	if not os.path.exists(listfile):
		raise StandardError('No correct distfile found')

	# determine path for the jail
	buildJail = env['JAIL_BASE_DIR'] + buildId[:env['BUILD_ID_SHORT_LENGTH']]

	print 'Building jail'
	# create jail and copy src code into jail
	subprocess.call([path(SCRIPT_FILE, env), buildJail, sourceCodeFolder, listfile]);
	print 'Jail constructed'

	return dict(buildJail = buildJail)

def path(path, env):
	return path.replace('$APP', env['APPLICATION_PATH'])

def executeBuild(db, buildId, buildArgs, env):
	# build command
	command = ["chroot", buildArgs['buildJail']]
	command.extend(getInvokeCommand(path=USER_SCRIPT_PATH))

	## ---- BUILD SECTION ----
	print 'Spawning build'
	p = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)

	# update the buid in the database (for the scheduler)
	db(db.current_builds.BuildId == buildId).update(PID=p.pid, start_time=datetime.datetime.today())
	db.commit()

	# wait until the build has finished
	p.wait()
	print 'Build finished'

	errors = p.stderr.read()
	output = p.stdout.read()
	hadBuildErrors = False

	if p.returncode != 0:
		hadBuildErrors = True

		# killed by build_monitor
		if p.returncode == -9:
			errors='The build timed out!'
			raise env['BuildException'](stdout = output, stderr = errors, exceptionDescription = errors)


	return dict(
		stdout = output,
		stderr = errors,
		)

def grading(db, buildId, project, course, user, buildArgs, env):
	enrollmentId = db((db.enrollment.student == user) & (db.enrollment.course == course)).select().first().id
	exerciseCourseId = db((db.course_exercise.exercise == project) & (db.course_exercise.course == course)).select().first().id

	grading = db.grading.insert(enrollment=enrollmentId, exercise=exerciseCourseId, unique_identifier=(str(enrollmentId) + '::' + str(exerciseCourseId)))

	if os.path.exists(buildArgs['buildJail'] + '/' + GRADING_FILE):
		grades = open(buildArgs['buildJail'] + '/' + GRADING_FILE)
		lines = grades.read().strip().split('\r')
		for assessment in lines:
			pointId, passed = assessment.strip().split(':')
			db.points_grading.insert(grading=grading, points=pointId, succeeded=(passed=='1'))
	else:
		db(db.current_builds.BuildId == buildId).update(buildError=True, error='No grading file found', finished=True)

def cleanup(db, buildId, buildArgs, sourceCodeFolder, env):
	cleanupProcess = subprocess.Popen([path(CLEANUP_FILE, env), buildArgs['buildJail'], sourceCodeFolder])
	cleanupProcess.wait()

def mainFile():
	return USER_SCRIPT_PATH


def binary():
	return 'python'

def getInvokeCommand(path):
	return  [binary(), path]

def buildAssertion(function_name, arguments, expected_result):
	output = '\t	assert ' + function_name + '( ' + arguments + ' )' + ' == ' + expected_result + '\r\n'
	return output;

def buildPointSet(id, assertions):
	output =  'try:' + '\r\n'

	output += '\r\n'.join(assertions)

	#output += '\t	assert ' + function_name + '( ' + arguments + ' )' + ' == ' + expected_result + '\r\n'
	output +=  'except Exception, e:' + '\r\n'
	output += '\t	print "failed"' + '\r\n'
	output += '\t	rating.write("' + str(id) + ':0\\r\\n")' + '\r\n'
	output +=  'else:' + '\r\n'
	output += '\t	print "passed"' + '\r\n'
	output += '\t	rating.write("' + str(id) + ':1\\r\\n")' + '\r\n'
	return output;

def buildTests(points):
	output =  'rating = open(\'' + GRADING_FILE + '\', \'w\')\r\n'
	output += ''
	output += '\r\n'.join(points)
	output += 'rating.close()\r\n'
	return output