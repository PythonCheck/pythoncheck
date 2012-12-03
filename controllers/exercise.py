def index():
	redirect(URL('list'))

@requires_role('teacher')
def list():
	exercise_list = SQLFORM.smartgrid(db.exercise, headers={'exercise.id':'#'})
	return locals()
