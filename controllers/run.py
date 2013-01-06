# coding: utf8
import subprocess
import platform
import random
import string
import runsystem as runsystem

from subprocess import PIPE
from gluon.serializers import json

@auth.requires_login()
def submit():
	project=request.vars.project
	course=request.vars.course
	main=request.vars.execute
	buildId = runsystem.generateBuildId(BUILD_ID_LENGTH)

	if len(course) == 0:
		raise HTTP(422, T('We can\'t do anything for you until you specify a course'))

	try:
		runsystem.invokeBuild(mode='submit', buildId=buildId, project=project, course=course, main=main, userId=auth.user_id)
	except Exception, e:
		raise HTTP(500, XML(json(dict(error=T('We got an error while trying to build the project: ') + T(str(e))))))
	

	return dict(mode='submit', buildId=buildId, timeout=CLIENT_TIMEOUT)


# user code is saved to database
# user code is run
# the output is caputured and replied
@auth.requires_login()
def run():
	buildId = runsystem.generateBuildId(BUILD_ID_LENGTH)
	project=request.vars.project
	course=request.vars.course
	main=request.vars.execute

	if len(course) == 0:
		course = None

	try:
		runsystem.invokeBuild(mode='test', buildId=buildId, main=main, project=project, course=course, userId=auth.user_id)
	except Exception, e:
		raise HTTP(500, XML(json(dict(error=T('We got an error while trying to build the project: ') + T(str(e))))))
	
	return dict(mode='run', buildId=buildId, timeout=CLIENT_TIMEOUT)


# the result of a build is fetched and retuned to the user
# if the buildId is unknown, an HTTP 422 error is raised
@auth.requires_login()
def result():
	data = db(db.current_builds.BuildId == request.vars.buildId).select().first()

	# if the data is not available throw an error
	if data == None:
		errorObject = {'message': T('Build ID does not exist')}
		raise HTTP(422, json(errorObject))

	# if data is available and the build has finsihed return the outputs
	if data.finished:
		out = dict(finished=data.finished, output=data.output, error=data.error)
		
		if data.buildError:
			raise HTTP(500, XML(json(out)))

		return out

	# if data is available and the build is still running tell the client to wait
	else:
		return dict(finished=data.finished, timeout=CLIENT_TIMEOUT)
