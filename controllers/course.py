def index():
	redirect(URL('list'))

def validate_new_course(form):
	form.vars.teacher = auth.user_id

@requires_role('student')
def list():
	new_form = SQLFORM(db.course, fields=['name'])
	if new_form.accepts(request.vars, session, onvalidation=validate_new_course):
		session.flash = T('Created course "') + new_form.vars.name + '"'
		redirect(URL('list'))
	elif new_form.errors:
		response.flash = T('Form has errors')

	course_list_contiditon = db.course if has_role('teacher') else ((db.enrollment.student == auth.user.id) & (db.course.id == db.enrollment.course))
	course_list_rows = db(course_list_contiditon).select()

	return dict(new_form = new_form,
				course_list_rows = course_list_rows)

###############################################################################

@requires_role('teacher')
def edit():
	record = db.course(request.args[0])
	if record.teacher != auth.user.id and has_role('admin') == False:
		session.flash = T('Unauthorized!')
		redirect(URL('list'))
	fields = ['name']
	grid = SQLFORM(db.course, record, fields=['name'])
	if grid.process().accepted:
		redirect(URL('view/' + request.args[0]))
	exercises = db(db.course_exercise.course == request.args(0)).select(orderby=db.course_exercise.start_date)
	students = db(db.enrollment.course == request.args(0)).select(orderby=db.enrollment.student)
	return locals()

###############################################################################

@requires_role('student')
def view():
	import datetime
	record = db.course(request.args(0)) or redirect(URL('list'))

	if record.teacher == auth.user.id and has_role('admin') != True:
		redirect(URL(request.application, 'course', 'edit/' + request.args(0)))
	elif db.enrollment(course=record.id, student=auth.user.id) is None and has_role('admin') == False:
		redirect(URL(request.application, 'user', 'not_authorized'))

	if has_role('teacher'):
		exercises = db(db.course_exercise.course == request.args(0)).select(orderby=db.course_exercise.start_date)
	else:
		exercises = db((db.course_exercise.course == request.args(0)) & (db.course_exercise.start_date <= datetime.datetime.now())).select(orderby=db.course_exercise.start_date)

	return dict(record = record,
				exercises = exercises,
				students = db(db.enrollment.course == request.args(0)).select(orderby=db.enrollment.student))