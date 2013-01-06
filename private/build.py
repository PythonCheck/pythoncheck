import sys
import subprocess
import platform
import datetime
import imp
import os

from subprocess import PIPE


GRADING_FILE = 'grades.grd'

## ---- ENVIRONMENT SECTION ----

args = sys.argv[1].split(' ')

# retrieve build id
buildId = args[0]

# retrieve source code file dir
srcCode = args[1]

# retrieve module path
modulePath = args[2]

# retrieve build mode
buildMode = args[3]

course, project, user = None, None, None

if buildMode == 'submit':
	course = args[4]
	project = args[5]
	user = args[6]

# retrieve build module
buildModule = imp.load_source('buildsystem.module', modulePath)

# determine distro and therefore distro's .list file
listfile = DISTOLIST_PATH + platform.dist()[0].lower() + "_" + platform.dist()[1].lower() + '.list'

## ---- PREPARING SECTION ----

# check if we found a valid listfile. if not generate an error and stop building
if not os.path.exists(listfile):
	db(db.current_builds.BuildId == buildId).update(buildError=True, error='No correct distfile found', finished=True)
	exit(1)

# determine path for the jail
buildJail = JAIL_BASE_DIR + buildId[:BUILD_ID_SHORT_LENGTH]

# create jail and copy src code into jail
subprocess.call([SCRIPT_FILE, buildJail, srcCode, listfile]);

# build command
command = ["chroot", buildJail]
command.extend(buildModule.getInvokeCommand(path=USER_SCRIPT_PATH))

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
hadBuildErrors = False

if p.returncode != 0:
	hadBuildErrors = True

	# killed by build_monitor
	if p.returncode == -9:
		errors='The build timed out!'

# update the database and distribute output
db(db.current_builds.PID==p.pid).update(output=p.stdout.read(), error=errors, finished=True, buildError=hadBuildErrors)
db.commit()

## ---- GRADING SECTION ----
if buildMode == 'submit':
	enrollmentId = db((db.enrollment.student == user) & (db.enrollment.course == course)).select().first().id
	exerciseCourseId = db((db.course_exercise.exercise == project) & (db.course_exercise.course == course)).select().first().id

	grading = db.grading.insert(course=enrollmentId, exercise=exerciseCourseId, unique_identifier=(str(enrollmentId) + '::' + str(exerciseCourseId)))

	if os.path.exists(buildJail + '/' + GRADING_FILE):
		grades = open(buildJail + '/' + GRADING_FILE)
		lines = grades.read().strip().split('\r')
		for assessment in lines:
			pointId, passed = assessment.strip().split(':')
			db.points_grading.insert(grading=grading, points=pointId, succeeded=(passed=='1'))
	else:
		db(db.current_builds.BuildId == buildId).update(buildError=True, error='No grading file found', finished=True)


## ---- CLEANUP SECTION ----

#cleanupProcess = subprocess.Popen([CLEANUP_FILE, buildJail, srcCode]);
#cleanupProcess.wait()



