import sys
import subprocess
import platform
import datetime
import imp
import os

from subprocess import PIPE

print 'Starting invocation'

## ---- ENVIRONMENT SECTION ----

args = sys.argv[1:]

# retrieve build id
buildId = args[0]

# retrieve source code file dir
srcCode = args[1]

# retrieve module path
modulePath = args[2]

APPLICATION_PATH = args[3]

# language
language = args[4]

# retrieve build mode
buildMode = args[5]

course, project, user = None, None, None

if buildMode == 'submit':
	course = args[6]
	project = args[7]
	user = args[8]

env = imp.load_source('env', APPLICATION_PATH + '/models/config.py')

sys.path.append(env.WEB2PY_PATH)

db = imp.load_source('env', APPLICATION_PATH + '/models/db.py').db

configVars = env.__dict__

# retrieve build module
buildModule = imp.load_source('buildsystem.module', modulePath + language.lower() + '.py')
BuildException = imp.load_source('BuildException', modulePath + 'BuildException.py').BuildException

## ---- PREPARING SECTION ----
try:
	buildArgs = buildModule.preBuild(db = db, buildId = buildId, sourceCodeFolder = srcCode, env = configVars)
except Exception, e:
	print str(e)
	db(db.current_builds.BuildId == buildId).update(buildError=True, error=str(e), finished=True)
	db.commit()
	exit(1)

buildResults = None

try:
	buildResults = buildModule.executeBuild(db, buildId = buildId, buildArgs = buildArgs, env = configVars)

# if a build error occurs
except BuildException, e:
	print str(e)
	db(db.current_builds.BuildId == buildId).update( \
		output=buildModule.output(db = db, buildId = buildId, buildArgs = buildArgs, env = configVars, output = e.stdout), \
		error=buildModule.error(db = db, buildId = buildId, buildArgs = buildArgs, env = configVars, error = e.stderr), \
		finished=True, \
		buildError=True)

except Exception, ex:
	print str(ex)
	db(db.current_builds.BuildId == buildId).update(output='', error='', finished=True, buildError=True)

# if the build finishes successfully
else:
	db(db.current_builds.BuildId == buildId).update( \
		output=buildModule.output(db = db, buildId = buildId, buildArgs = buildArgs, env = configVars, output = buildResults['stdout']), \
		error=buildModule.error(db = db, buildId = buildId, buildArgs = buildArgs, env = configVars, error = buildResults['stderr']), \
		finished=True, \
		buildError=False)

# commit
db.commit()

## ---- GRADING SECTION ----
if buildMode == 'submit':
	buildModule.grading(db = db, buildId = buildId, project = project, course = course, user = user, buildArgs = buildArgs, env = locals(), buildResults = buildResults)

db.commit()

## ---- CLEANUP SECTION ----
buildModule.cleanup(db = db, buildId = buildId, buildArgs = buildArgs, sourceCodeFolder = srcCode, env = configVars)

db.commit()





