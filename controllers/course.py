
def new():
	if db(auth.user_id == db.auth_membership.user_id).select()[0].group_id < 2:
		raise HTTP(403)
	form = SQLFORM(db.course, fields=['name'])
	if form.process().accepted:
		response.flash = ''
	elif form.errors:
		response.flash = 'form has errors'
	return dict(form=form)