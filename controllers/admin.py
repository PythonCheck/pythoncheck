@requires_role('admin')
def user():
	users = db(db.auth_user.id > 0).select(orderby=db.auth_user.last_name|db.auth_user.first_name)
	roles = db(db.auth_group.id > 0).select(orderby=db.auth_group.id)
	return locals()

@requires_role('admin')
def role():
	if db(db.auth_user.id == request.args(0)).count() < 1:
		session.flash = T('This user doesn\'t exist!')
	elif db(db.auth_group.id == request.args(1)).count() < 1:
		session.flash = T('This role doesn\'t exist!')
	else:
		db(db.auth_membership.user_id == request.args(0)).update(group_id=request.args(1))
		session.flash = T('Changed role!')
	redirect(URL('user'))