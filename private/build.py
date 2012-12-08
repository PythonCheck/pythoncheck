import sys
import subprocess
import platform
import datetime
import imp

from subprocess import PIPE

## CONFIG
JAIL_BASE_DIR = '/tmp/jails/' 
DISTOLIST_PATH = "/usr/share/web2py2/applications/PythonCheck/scripts/jail/"
SCRIPT_FILE = DISTOLIST_PATH + 'create.sh'
CLEANUP_FILE = DISTOLIST_PATH + 'cleanup.sh'
USER_SCRIPT_PATH = "/script.py"
BUILD_ID_LENGTH = 512
BUILD_ID_SHORT_LENGTH = 32

## ---- ENVIRONMENT SECTION ----

args = sys.argv[1].split(' ')

# retrieve build id
buildId = args[0]

# retrieve source code file dir
srcCode = args[1]

# retrieve module path
modulePath = args[2]

# retrieve build module
buildModule = imp.load_source('buildsystem.module', modulePath)

# determine distro and therefore distro's .list file
listfile = DISTOLIST_PATH + platform.dist()[0].lower() + "_" + platform.dist()[1].lower() + '.list'

## ---- PREPARING SECTION ----

# write into database before creating the jail
db.current_builds.insert(PID=None, BuildId=buildId, start_time=datetime.datetime.today())

# determine path for the jail
buildJail = JAIL_BASE_DIR + buildId[:BUILD_ID_SHORT_LENGTH]

# create jail and copy src code into jail
subprocess.call([SCRIPT_FILE, buildJail, srcCode, listfile]);

# build command
command = ["chroot", buildJail]
command.extend(buildModule.getInvokeCommand(path=USER_SCRIPT_PATH))

## ---- BUILD SECTION ----

p = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)

# update the buid in the database (for the scheduler)
db(db.current_builds.BuildId == buildId).update(PID=p.pid, start_time=datetime.datetime.today())
db.commit()

# wait until the build has finished
p.wait()

# update the database and distribute output
db(db.current_builds.PID==p.pid).update(output=p.stdout.read(), error=p.stderr.read(), finished=True)

## ---- CLEANUP SECTION ----

cleanupProcess = subprocess.Popen([CLEANUP_FILE, buildJail]);
cleanupProcess.wait()



