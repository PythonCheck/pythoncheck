def index():
	redirect(URL('list'))

@requires_role('teacher')
def list():
	if request.args and request.args[0] == 'new':
		redirect(URL(request.application, request.controller, 'new'))
		return
	editable = auth.has_membership('admin')
	deletable = auth.has_membership('admin')
	return dict(grid = SQLFORM.grid(db.course, headers={'course.id':'#'}, orderby='course.name', create=True, editable=editable, deletable=deletable))

###############################################################################

def validate_new_user(form):
	form.vars.teacher = auth.user_id

@requires_role('teacher')
def new():
	form = SQLFORM(db.course, fields=['name'])
	if form.accepts(request.vars, session, onvalidation=validate_new_user):
		session.flash = 'Created course "' + form.vars.name + '"'
		redirect(URL(list))
	elif form.errors:
		response.flash = 'form has errors'
	return dict(form=form)