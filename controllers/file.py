from datetime import datetime
from array import array

# opens a file
@auth.requires_login()
def open():
	return details()

# opens a file
@auth.requires_login()
def details(filename=None, course=None, project=None, includeContent=True):

	result = None

	if (filename == None) | (course == None) | (project == None):
		course = request.args[0]
		project = request.args[1]
		if len(request.args) > 2:
			filename = request.args[2]

		if filename == None:
			filename = project
			project = course
			course = None

	query = (db.files.filename == filename) & (db.files.project == project)	

	if (course == None) | (course == False):
		result = db(query & (db.files.projectIsExercise == False)).select()
	else:
		result = db(query & (db.files.projectIsExercise == True) & (db.files.course == course)).select()

	result = result.first().as_dict()

	if includeContent == False:
		result.pop('content', None)

	path = []

	if result['projectIsExercise']:
		path.append(str(result['course']))

	path.append(str(result['project']))
	path.append(result['filename'])

	result['readURL'] = 'file/open/' + '/'.join(path)
	result['saveURL'] = 'file/save/' + '/'.join(path)

	result.pop('projectIsExercise', False)
	result.pop('user', False)

	response.view = 'file/open.json'
	return result

# saves a file
@auth.requires_login()
def save():
	project = request.vars.project
	course = request.vars.course
	filename = request.vars.filename
	code = request.vars.code

	if len(db((db.files.filename == filename) & (db.files.user == auth.user_id) & (db.files.project == project)).select()) != 1:
		raise HTTP(422, 'invalid file identifier. file does not exist')

	dbfile = db((db.files.filename == filename) & (db.files.user == auth.user_id) & (db.files.project == project)).update(content=code)

	response.view = 'file/save.json'
	return dict(success=True)

@auth.requires_login()
def new():
	filename = request.vars.filename
	filetype = request.vars.type
	project = request.vars.project
	course = request.vars.course

	uniqueIdentifier = str(filename) + '::' + str(course) + '::' + str(project) + '::' + str(auth.user_id)	

	if filetype == 'project':
		if (project == None) or (project.find('/') >= 0):
			raise HTTP(422, 'invalid project identifier')
		else:
			try:
				db.files.insert(unique_identifier=uniqueIdentifier, user=auth.user_id, filename=filename, project=project, projectIsExercise=False, edited=datetime.today(), course=None)
			except Exception, e:
				raise HTTP(422, 'invalid filename: file exists')
			
	
	elif filetype == 'exercise':

		if not(project.isdigit()):
			raise HTTP(422, 'project must be a valid exercise number')

		elif not(course.isdigit()):
			raise HTTP(422, 'course must be a valid course number')

		elif len( \
			db((db.course_exercise.exercise==project) & \
			(db.course_exercise.course==course) & \
			(db.enrollment.course==course) & \
			(db.enrollment.student==auth.user_id)).select()) != 1:

			raise HTTP(422, 'This exercise and course don\'t not exist and therefore we can\'t create a file in it')

		else:
			try:
				db.files.insert(unique_identifier=uniqueIdentifier, user=auth.user_id, filename=filename, project=project, projectIsExercise=True, edited=datetime.today(), course=course)
			except Exception, e:	
				raise HTTP(422, 'invalid filename: file exists')

			
	else:
		raise HTTP(422, 'no valid filetype specified. please either use project or exercise')

	return dict(success=True)

def list():
	files = dict()
	current = dict()

	files['courses'] = dict()
	courses = db(db.enrollment.student == auth.user_id).select(db.course.id, db.course.name, join=db.course.on(db.course.id==db.enrollment.course))
	for course in courses:
		files['courses'][course.name] = dict()
		files['courses'][course.name]['exercises'] = dict()

		exercises = db((db.enrollment.student == auth.user_id) & (db.enrollment.course == course)).select(db.course_exercise.exercise)

		for exercise in exercises:
			exerciseName = db(db.exercise.id==exercise.exercise).select().first().name

			files['courses'][course.name]['exercises'][exerciseName] = dict()
			files['courses'][course.name]['exercises'][exerciseName]['files'] = dict()

			filesPerExercise = db((db.enrollment.student == auth.user_id) & (db.enrollment.course == course) & (db.files.project == exercise.exercise) & (db.files.projectIsExercise == True)).select()

			for singleFile in filesPerExercise:
				files['courses'][course.name]['exercises'][exerciseName]['files'][singleFile.files.filename] = details(filename=singleFile.files.filename, project=exercise.exercise, course=course.id, includeContent=False)


	projects = db((db.files.user == auth.user_id) & (db.files.projectIsExercise == False)).select(db.files.project, distinct=True)

	files['projects'] = dict()

	for project in projects:
		files['projects'][project.project] = dict()
		files['projects'][project.project]['files'] = dict()

		for singleFile in db((db.files.user == auth.user_id) & (db.files.projectIsExercise == False) & (db.files.project == project.project)).select():
			files['projects'][project.project]['files'][singleFile.filename] = details(filename=singleFile.filename, project=project.project, course=False, includeContent=False)

	return files