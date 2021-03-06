# coding: utf8
 
# register a user
def register():
    form=auth.register(next=auth.settings.register_next)
    return dict(form=form)

def login():
	if auth.user_id:
		redirect(URL('user', 'me'))
	return dict(form=auth.login())

@auth.requires_login()
def logout():
	return dict(form=auth.logout())	

def not_authorized() :
	return dict(form=auth.not_authorized())

@auth.requires_login()
def me():
	return dict()

@auth.requires_login()
def change_password():
	return dict(form=auth.change_password())
