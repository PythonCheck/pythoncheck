# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = ' '.join(
    word.capitalize() for word in request.application.split('_'))
response.subtitle = T('customize me!')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Your Name <you@example.com>'
response.meta.description = 'a cool new app'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [  ]

if has_role( 'teacher' ):
	response.menu.append( ( T( 'Exercise Pool' ), False, URL( 'exercise', 'list' ), [  ] ) )
	response.menu.append( ( T( 'Courses' ), False, URL( 'course', 'list' ), [  ] ) )
elif has_role( 'student' ):
	response.menu.append( ( T( 'Me' ), False, URL( 'user', 'me' ), [  ] ) )
	response.menu.append( ( T( 'My Courses' ), False, URL( 'course', 'list' ), [  ] ) )
	response.menu.append( ( T( 'My Exercises' ), False, URL( 'exercise', 'list' ), [  ] ) )


response.menu.append( ( T( 'IDE' ), False, URL( 'default', 'index' ), [  ] ) )

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################


def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu.append(('Courses', False, URL(app, 'course', 'list')))
    response.menu.append(('Exercises', False, URL(app, 'exercise', 'list')))
# _()
