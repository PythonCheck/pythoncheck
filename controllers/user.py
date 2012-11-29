# coding: utf8
 
# register a user
def register():
    form=auth.register()
    return dict(form=form)

def login():
	return dict(form=auth.login())
