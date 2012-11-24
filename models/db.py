# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = False
auth.settings.register_onaccept = (lambda f: auth.add_membership(auth.id_group('student'), auth.user_id))

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.define_table('course', 
                Field('name', 
                      'string', 
                       length=50, 
                       required=True, 
                       unique=True,
                       label=T('Name')),
                Field('teacher',
                      'reference auth_user',
                       required=True,
                       label=T('Teacher')))

db.course.teacher.requires = IS_IN_DB(db, db.auth_user.id)

db.define_table('language', 
    Field('name', 'string', length=50, required=True, unique=True), 
    Field('description', 'string', required=False, unique=False), 
    primarykey=['name'])

db.define_table('exercise',
    Field('name', 'string', length=50, required=True, unique=True),
    Field('text', 'string', required=False, unique=False),
    Field('language', requires=[IS_IN_DB(db, db.language.name)]),
    primarykey=['name', 'language'])

db.define_table('code', 
    Field('version', 'integer', required=True), 
    Field('code', required=True), 
    Field('exercise', requires=[IS_IN_DB(db, db.exercise.name)]), 
    Field('course', requires=[IS_IN_DB(db, db.course.name)]), 
    Field('language', requires=[IS_IN_DB(db, db.language.name)]),
    Field('user', 'integer', required=True, requires=[IS_IN_DB(db, db.auth_user.id)]),
    primarykey=['version', 'exercise', 'course', 'language', 'user'])






def requires_role(role):
    def decorator(fn):
        def f():
            if hasattr(auth.user_groups, 'values') and len(auth.user_groups.values()) > 0:
                roleId = db(db.auth_group.role.like(role.lower())).select()[0].id
                for group_key in auth.user_groups.keys():
                    if group_key >= roleId:
                        return fn()
                else:
                    redirect(URL(request.application, 'default/user', 'not_authorized'))
            else:
                redirect(URL(request.application, 'default/user', 'login?_next=' + request.env.path_info))
        return f
    return decorator