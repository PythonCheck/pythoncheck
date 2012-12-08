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

@auth.requires_login()
def submit():
	print "Hi. We will now run the test."

	# src=request.vars.code;
	# language=request.vars.language
	project=request.vars.project
	course=request.vars.course
	main=request.vars.execute
	buildId = runsystem.generateBuildId(BUILD_ID_LENGTH)

	runsystem.invokeBuild(mode='submit', buildId=buildId, project=project, course=course, main=main)




# user code is saved to database
# user code is run
# the output is caputured and replied
@auth.requires_login()
def run():
	# src=request.vars.code

	buildId = runsystem.generateBuildId(BUILD_ID_LENGTH)
	project=request.vars.project
	course=request.vars.course
	main=request.vars.execute

	if len(course) == 0:
		print 'course no exist'
		course = None

	runsystem.invokeBuild(mode='test', buildId=buildId, main=main, project=project, course=course)
	
	return dict(mode='run', buildId=buildId, timeout=CLIENT_TIMEOUT)


# the result of a build is fetched and retuned to the user
# if the buildId is unknown, an HTTP 422 error is raised
@auth.requires_login()
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
