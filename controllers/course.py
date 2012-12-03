def index():
	redirect(URL('list'))

@requires_role('teacher')
def list():
	if request.args:
		if request.args[0] == 'new':
			redirect(URL(request.application, request.controller, 'new'))
		elif request.args[0] == 'edit':
			redirect(URL(request.application, request.controller, 'edit/' + request.args[2]))
		elif request.args[0] == 'view':
			redirect(URL(request.application, request.controller, 'view/' + request.args[2]))
	editable = auth.has_membership('admin')
	deletable = auth.has_membership('admin')
	return dict(grid = SQLFORM.grid(db.course, 
									headers={'course.id':'#'}, 
									orderby='course.name', 
									editable=lambda row: auth.has_membership('admin') or row.teacher == auth.user.id,
									deletable=lambda row: auth.has_membership('admin') or row.teacher == auth.user.id))

###############################################################################

def validate_new_user(form):
	form.vars.teacher = auth.user_id

@requires_role('teacher')
def new():
	form = SQLFORM(db.course, fields=['name'])
	if form.accepts(request.vars, session, onvalidation=validate_new_user):
		session.flash = 'Created course "' + form.vars.name + '"'
		redirect(URL('list'))
	elif form.errors:
		response.flash = 'form has errors'
	return dict(form=form)

###############################################################################

@requires_role('teacher')
def edit():
	record = db.course(request.args(0)) or redirect(URL('list'))
	if record.teacher != auth.user.id and auth.has_membership('admin') == False:
		session.flash = 'Unauthorized!'
		redirect(URL('list'))
	fields = ['name']
	grid = SQLFORM(db.course, record, fields=['name'])
	if grid.process().accepted:
		redirect(URL('view/' + request.args[0]))
	return locals()

###############################################################################

@requires_role('student')
def view():
	record = db.course(request.args(0)) or redirect(URL('list'))
	course_info = SQLFORM(db.course, record, readonly=True)

	exercises = db(db.course_exercise.course == request.args[0]) 			\
					.select(db.course_exercise.exercise, 					\
							db.course_exercise.start_date, 					\
							db.course_exercise.end_date,					\
							orderby=db.course_exercise.start_date)

	students = db((db.auth_user.id == db.enrollment.student) & (db.enrollment.course == request.args(0))) \
					.select(db.auth_user.id,								\
						    db.auth_user.last_name,							\
						    db.auth_user.first_name,						\
						    orderby=[db.auth_user.last_name, db.auth_user.first_name])

	return dict(course_info=course_info,
				exercises=SQLTABLE(exercises, headers='labels'),
				students=SQLTABLE(students, headers='labels'))