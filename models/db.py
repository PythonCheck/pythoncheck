# -*- coding: utf-8 -*-
from imp import load_source
import os

## has to stay in there!!!!
runningModelStandalone = not 'request' in globals()

if runningModelStandalone:
    from gluon.dal import DAL, Field
    global db

    def T(str):
        return T

    config = load_source('config', os.path.dirname(locals()['__file__']) + '/config.py')

    db = DAL(config.DB_CONNECTION, folder=config.APPLICATION_PATH + '/databases')

elif not request.env.web2py_runtime_gae:

    ## if NOT running on Google App Engine use SQLite or other DB
    # db = DAL('sqlite://storage.sqlite')
    db = DAL(DB_CONNECTION)
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

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

if not runningModelStandalone:
    from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
    auth = Auth(db)
    crud, service, plugins = Crud(db), Service(), PluginManager()

    ## create all tables needed by auth if not custom tables
    auth.define_tables(username=True, signature=False)


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
    Field('student', 'integer', required=True, label=T('Student')),
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
    Field('user', 'reference auth_user', required=True))

db.define_table('files',
    Field('unique_identifier', required=True, unique=True),
    Field('user', 'reference auth_user', required=True),
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

if not runningModelStandalone:
    ### default values
    ## groups
    db.auth_group.update_or_insert(id=1, role='Student')
    db.auth_group.update_or_insert(id=2, role='Teacher')
    db.auth_group.update_or_insert(id=3, role='Admin')
    ## programming languages
    db.language.update_or_insert(name='Python')
