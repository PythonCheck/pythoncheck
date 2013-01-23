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
		raise HTTP(422, XML(json(dict(error=T('We can\'t do anything for you until you specify a course')))))

	try:
		runsystem.invokeBuild(mode='submit', buildId=buildId, project=project, course=course, main=main, userId=auth.user_id, appPath=APPLICATION_PATH)
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
		runsystem.invokeBuild(mode='test', buildId=buildId, main=main, project=project, course=course, userId=auth.user_id, appPath=APPLICATION_PATH)
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

# retrieve the grading of a user and exercise
def _grading(userId, course, exercise):

	response = dict()

	enrollment = db((db.enrollment.course == course) & (db.enrollment.student == userId)).select()

	# no enrollment found
	if len(enrollment) < 1:
		response['error'] = T('You are not enrolled to the course you tried to get grades for')
		raise HTTP(422, XML(json(response)))

	exerciseAssignment = db((db.course_exercise.exercise == exercise) & (db.course_exercise.course == course)).select()

	# no enrollment found
	if len(exerciseAssignment) < 1:
		response['error'] = T('There is no such exercise in this course')
		raise HTTP(422, XML(json(response)))

	exerciseAssignment = exerciseAssignment.first()

	grades = db((db.grading.enrollment == enrollment.first()) & (db.grading.exercise == exerciseAssignment.id)).select()

	# no grades found
	if len(grades) < 1:
		response['error'] = T('It seems like there is no grading for this exercise')
		raise HTTP(422, XML(json(response)))

	# in an exercise is assigned multiple times
	response['grades'] = []
	for grade in grades:
		# get the point groups
		currentGrading = dict()
		pointGroups = db((db.points_grading.grading == grade.id)).select()
		
		currentGrading['overallPoints'] = 0
		currentGrading['pointGroups'] = []

		# iterate over them and build processable dicts
		for pointGroup in pointGroups:
			# fetch the referenced point group to gather data
			referencedPointGroup = db((db.points.id == pointGroup.points)).select().first()

			currentGrading['pointGroups'].append(dict(number=referencedPointGroup.number_of_points, passed=pointGroup.succeeded))
			
			# sum up the results
			if pointGroup.succeeded:
				currentGrading['overallPoints'] += referencedPointGroup.number_of_points

		# put the grading into the array
		response['grades'].append(currentGrading)

	return response	

# exposes grading
def grading():
	userId = auth.user_id
	course = request.vars.course
	exercise = request.vars.exercise

	return _grading(userId = userId, course = course, exercise = exercise)

	



