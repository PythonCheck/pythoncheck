def index():
	redirect(URL('list'))

@requires_role('teacher')
def list():
	exercises = db().select(db.exercise.ALL)
	return locals()

@requires_role('teacher')
def new():
	form = SQLFORM(db.exercise, fields=['name', 'language', 'text', 'preset'])
	if form.process().accepted:
		session.flash = T('Created Exercise »%(exercise_name)s«') % { 'exercise_name' : form.vars.name }
		redirect(URL('assertions/' + str(form.vars.id)))
	elif form.errors:
		session.flash = form.errors
	return locals()

@requires_role('teacher')
def edit():
	record = db.exercise(request.args(0))
	form = SQLFORM(db.exercise, record, fields=['name', 'language', 'text', 'preset'])
	if form.process().accepted:
		session.flash = 'OK'
		redirect(URL('list'))
	elif form.errors:
		response.flash = 'There were errors!'
	return locals()

def validate_new_assertion(form):
	print form.vars.function_call
	return False

import re

@requires_role('teacher')
def assertions():
	exercise = db.exercise(request.args(0))
	point_groups = db(db.points.exercise == exercise.id).select().sort(lambda row: ~row.number_of_points)
	if request.args(1) == 'remove':
		db(db.assertion.id == request.args(2)).delete()
		session.flash = 'Removed Assertion!'
		redirect(URL('assertions/' + request.args(0)))
	if 'new_assertion_submit' in request.vars:
		function_call = request.vars['function_call']
		expected_result = request.vars['expected_result']
		if re.compile('^\w.+\(.*\)$').match(function_call) and re.compile('^.+$').match(expected_result):
			db.assertion.insert(points=request.vars['point_group'], 
								function_name=function_call[:function_call.index('(')],
								arguments=function_call[function_call.index('(')+1:function_call.rindex(')')],
								expected_result=expected_result)
			response.flash = 'Created Assertion!'
		else:
			response.flash = 'Couldn\'t create Assertion!'

	# new_assertion = SQLFORM(db.assertion)
	# # if form.accepts(request.vars, session, formname='new_assertion', onvalidation=validate_new_assertion):
	# if new_assertion.process(formname='new_assertion', onvalidation=validate_new_assertion).accepted:
	# 	print 'acc'
	# 	pass
	# else:
	# 	print new_assertion.vars
	return locals()