# -*- coding: utf-8 -*-
from gluon.custom_import import track_changes; track_changes(True)
#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    # db = DAL('sqlite://storage.sqlite')
    db = DAL('mysql://school:school@localhost/school')
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


def process_login_accept(f):
    user_has_membership = db(db.auth_membership.user_id == auth.user_id)
    if user_has_membership.count() < 1:
        import re
        group_id = 1 if re.compile('^\d+$').match(f.vars['username']) else 2
        db.auth_membership.insert(user_id=auth.user_id,
                                  group_id=group_id)
    print f.vars;


from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
from gluon.contrib.login_methods.ldap_auth import ldap_auth
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
# auth.define_tables(username=False, signature=False
auth.define_tables(username=True)
auth.settings.create_user_groups=False
# all we need is login
auth.settings.actions_disabled=['register','change_password','request_reset_password','retrieve_username']

# you don't have to remember me
auth.settings.remember_me_form = False

auth.settings.login_methods = [ldap_auth(mode='ad',
   server='deepspace.htlw3r.ac.at',
   # server='localhost',
   base_dn='dc=htlw3r,dc=ac,dc=at',
   manage_user=True,
   user_firstname_attrib='givenName',
   user_lastname_attrib='sn',
   db=db)]


## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.logged_url = URL(c='default', f='index') # if accessing register or similar as logged in user redirect to the me page
auth.settings.login_next = URL(c='default', f='index') 
auth.settings.controller = 'user'
auth.settings.register_next = URL(c='default', f='index')
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = False
auth.settings.register_onaccept = (lambda f: auth.add_membership(1, auth.user_id))
auth.settings.login_onaccept = (process_login_accept)

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
                       label=T('Teacher')),
                format='%(name)s')

db.define_table('language', 
    Field('name', 'string', length=50, required=True, unique=True), 
    Field('description', 'string', required=False, unique=False),
    format='%(name)s')

db.define_table('exercise',
    Field('name', 'string', length=50, required=True, unique=True),
    Field('language', db.language, required=True),
    Field('text', 'text', required=True, unique=False),
    Field('preset', 'text', required=False, unique=False),
    format='%(name)s (%(language)s)')

db.define_table('course_exercise',
    Field('exercise', db.exercise, required=True, label=T('Excercise')),
    Field('course', db.course, required=True, label=T('Course')),
    Field('start_date', 'datetime', required=True, label=T('Start Date')),
    Field('end_date', 'datetime', required=True, label=T('Due Date')),
    format='%(exercise)s in %(course)s (%(start_date)s - %(end_date)s)')

db.define_table('enrollment',
    Field('course', db.course, required=True, label=T('Course')),
    Field('student', db.auth_user, required=True, label=T('Student')),
    format='%(student)s in %(course)s')

db.define_table('points',
    Field('number_of_points', 'integer', required=True, label=T('Number of Points')),
    Field('exercise', db.exercise, required=True, label=T('Exercise')),
    format='Exercise %(exercise)s: %(number_of_points)s points')

db.define_table('assertion',
    Field('function_name', required=True, label=T('Function Name')),
    Field('arguments', label=T('Arguments')),
    Field('expected_result', required=True, label=T('Expected Result')),
    Field('points', db.points, label=T('Points')),
    format='%(points)s | %(function_name)s(%(arguments)s) => %(expected_result)s')

db.define_table('current_builds',
    Field('PID', 'integer', required=True),
    Field('BuildId', 'string', required=True, unique=True),
    Field('start_time', 'datetime', required=True),
    Field('finished', 'boolean', required=False, default=False),
    Field('output', 'text', required=False),
    Field('error', 'text', required=False),
    Field('buildError', 'boolean', required=False),
    Field('user', db.auth_user, required=True))

db.define_table('files',
    Field('unique_identifier', required=True, unique=True),
    Field('user', db.auth_user, required=True),
    Field('filename', 'string', required=True),
    Field('edited', 'datetime', required=True, default='now()'),
    Field('course', 'integer', required=False),
    Field('project', 'string', required=True),
    Field('projectIsExercise', 'boolean', required=True),
    Field('content', 'text'),
    Field('version', 'integer'),
    Field('writeable', 'boolean', required=True, default=True))

db.define_table('grading', 
    Field('enrollment', db.enrollment, required=True), # contains the userid
    Field('exercise', db.course_exercise, required=True),
    Field('unique_identifier', 'string', unique=True, required=True))

db.define_table('points_grading', 
    Field('grading', db.grading, required=True),
    Field('points', db.points, required=True), 
    Field('succeeded', 'boolean', required=True, default=False))

### default values
## groups
db.auth_group.update_or_insert(id=1, role='Student')
db.auth_group.update_or_insert(id=2, role='Teacher')
db.auth_group.update_or_insert(id=3, role='Admin')
## programming languages
db.language.update_or_insert(name='Python')


@auth.requires_login()
def requires_role(role):
    def decorator(fn):
        def f():
            hasRole = has_role(role)
            if hasRole is None:
                redirect(URL(request.application, 'user', 'login?_next=' + request.env.path_info))
            elif hasRole == True:
                return fn()
            else:
                redirect(URL(request.application, 'user', 'not_authorized'))
        return f
    return decorator

def has_role(role):
    if hasattr(auth.user_groups, 'values') and len(auth.user_groups.values()) > 0:
        roleId = db(db.auth_group.role.like(role.lower())).select()
        if roleId:
            roleId = roleId[0].id
            for group_key in auth.user_groups.keys():
                if group_key >= roleId:
                    return True
            else:
                return False
        else:
            return False
    return None