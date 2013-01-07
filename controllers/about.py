def index():
	return dict( \
		peopleCaption=T('These are the people, that have helped to create this plattform'),
		people=[dict(name='Jonas Keisel', job=T('Programmer')), \
				dict(name='Daniel Laxar', job=T('Programmer')), \
				dict(name='Tobias Primus', job=T('Project Manager')), \
				dict(name='Armin Redzic', job=T('Layout & Design'))] \
		)

def legal():
	return dict()