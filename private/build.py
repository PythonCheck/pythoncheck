import sys
import subprocess
import platform
import datetime
import imp
import os

from subprocess import PIPE

print 'Starting invocation'


GRADING_FILE = 'grades.grd'

## ---- ENVIRONMENT SECTION ----

args = sys.argv[1].split(' ')

# retrieve build id
buildId = args[0]

# retrieve source code file dir
srcCode = args[1]

# retrieve module path
modulePath = args[2]

# language
language = args[3]

# retrieve build mode
buildMode = args[4]

course, project, user = None, None, None

if buildMode == 'submit':
	course = args[5]
	project = args[6]
	user = args[7]

# retrieve build module
buildModule = imp.load_source('buildsystem.module', modulePath + language.lower() + '.py')
BuildException = imp.load_source('BuildException', modulePath + 'BuildException.py').BuildException

## ---- PREPARING SECTION ----
try:
	buildArgs = buildModule.preBuild(db = db, buildId = buildId, sourceCodeFolder = srcCode, env = locals())
except Exception, e:
	db(db.current_builds.BuildId == buildId).update(buildError=True, error=str(e), finished=True)
	exit(1)

buildResults = None

try:
	buildResults = buildModule.executeBuild(db, buildId = buildId, buildArgs = buildArgs, env = locals())

# if a build error occurs
except BuildException, e:
	print str(e)
	db(db.current_builds.BuildId == buildId).update(output=e.stdout, error=e.stderr, finished=True, buildError=True)

except Exception, ex:
	print str(ex)

# if the build finishes successfully
else:
	db(db.current_builds.BuildId == buildId).update(output=buildResults['stdout'], error=buildResults['stderr'], finished=True, buildError=False)

buildJail = buildArgs['buildJail']

# commit
db.commit()

## ---- GRADING SECTION ----
if buildMode == 'submit':
	buildModule.grading(db = db, buildId = buildId, project = project, course = course, user = user, buildArgs = buildArgs, env = locals())


## ---- CLEANUP SECTION ----
buildModule.cleanup(db = db, buildId = buildId, buildArgs = buildArgs, sourceCodeFolder = srcCode, env = locals())





