###
### most common settings
###

# application name
APP_NAME = 'PythonCheck'

# directories the jails are created in
JAIL_BASE_DIR = '/tmp/jails/' 

# path to the application in the web2py folder
APPLICATION_PATH = '/usr/share/web2py2/applications/' + APP_NAME

# path to the web2py binary/.py-file
WEB2PY_BIN = '/usr/share/web2py2/web2py.py'

# directory the scripts of the user are stored temporarily
SRC_DIR = '/res/scripts/'

###
### build settings
###

# depends on the speed of the server. this should be the average build time of a project
CLIENT_TIMEOUT = 1500
MAX_BUILD_TIME = 10 # specify in seconds


###
### change only if you relocate the distolitsts, the jail-files or the build scripts
###

# path where the distrolists are located
DISTOLIST_PATH = APPLICATION_PATH + '/scripts/jail/' 

# path of the create script that creates the jail
SCRIPT_FILE = DISTOLIST_PATH + 'create.sh'

# path of the cleanup script that cleans up a build
CLEANUP_FILE = DISTOLIST_PATH + 'cleanup.sh'

# path of the build script responsible for the build
BUILD_SCRIPT = APPLICATION_PATH + '/private/build.py'

###
### don't change if you don't know what you're doing
###

## JAIL SETTINGS 
# location of the main script in the jail 
USER_SCRIPT_PATH = '/script.py'

###
### rarely changed
###

## BUILDID Settings
# the length of the whole buildID
BUILD_ID_LENGTH = 512
# the length of the shortened buildID used in the filesystem
BUILD_ID_SHORT_LENGTH = 32

###
### really dangerous to change. Vary the behaviour of the application
###
EXERCISE_CONTAINS_SINGLE_FILE = True
EXERCISE_MAIN_FILE = 'main.py'