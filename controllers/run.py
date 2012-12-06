# coding: utf8
import subprocess
import platform
import random
import string
import run as runsystem

from subprocess import PIPE
from gluon.serializers import json

## CONFIG
BUILD_ID_LENGTH = 512
CLIENT_TIMEOUT = 1500

def submit():
	print "Hi. We will now run the test."

	src=request.vars.code;
	language=request.vars.language
	exercise=request.vars.exercise
	course=request.vars.course
	buildId = runsystem.generateBuildId(BUILD_ID_LENGTH)

	runsystem.invokeBuild(code=src, mode='submit', buildId=buildId, exercise=exercise, course=course, language=language)




# user code is saved to database
# user code is run
# the output is caputured and replied
def run():
	src=request.vars.code
	buildId = runsystem.generateBuildId(BUILD_ID_LENGTH)

	runsystem.invokeBuild(code=src, mode='test', buildId=buildId)
	
	return dict(mode='run', buildId=buildId, timeout=CLIENT_TIMEOUT)



# the result of a build is fetched and retuned to the user
# if the buildId is unknown, an HTTP 422 error is raised
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
