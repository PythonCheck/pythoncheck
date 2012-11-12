# coding: utf8
# try something like
def register():
    T.force('de')
    form=FORM(
        T('First Name'),
        INPUT(_name='first_name', requires=IS_NOT_EMPTY()),
        T('Last Name'),
        INPUT(_name='last_name', requires=IS_NOT_EMPTY()),
        T('Email'),
        INPUT(_name='email', requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'auth_user.email'), IS_EMAIL()]),
        INPUT(_name='password', _type='password', requires=[IS_NOT_EMPTY(), IS_LENGTH(minsize=6)]),
        INPUT(_name='rpassword', _type='password', requires=[IS_NOT_EMPTY(), IS_EQUAL_TO(request.vars.password)]),
        INPUT(_type='submit')
    )
    return dict(form=form)
