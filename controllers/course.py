
def validate_new_user(form):
	form.vars.teacher = auth.user_id

def new():
	if auth.user_id is None or db(auth.user_id == db.auth_membership.user_id).select()[0].group_id < 2:
		raise HTTP(403)
	form = SQLFORM(db.course, fields=['name'])
	if form.accepts(request.vars, session, onvalidation=validate_new_user):
		response.flash = 'Created course "' + form.vars.name + '"'
		redirect(URL(list))
	elif form.errors:
		response.flash = 'form has errors'
	return dict(form=form)
