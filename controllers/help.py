def index():
	redirect(URL('general'))

def general():
	return dict(topics=[ dict(text=T('Users'), url=URL('users')) ])

def users():
	return dict()