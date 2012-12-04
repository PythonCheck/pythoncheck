import sys
import subprocess
import platform
import datetime

from subprocess import PIPE

file=open('/hi.file', 'w')

for str in sys.argv:
	file.write(str + '\n\r')

file.write('output of script ---------------------\r\n')

JAIL_DIR = "/tmp/jail" 
SRC_DIR = "/res/scripts/"
WEB2PY_BIN = '/usr/share/web2py2/web2py.py'
DISTOLIST_PATH = "/usr/share/web2py2/applications/PythonCheck/scripts/jail/"
SCRIPT_FILE = DISTOLIST_PATH + "create.sh"
CLEANUP_FILE = DISTOLIST_PATH + 'cleanup.sh'
USER_SCRIPT_PATH = "/script.py"

# retrieve build id and insert into database
buildId = sys.argv[1]
db.current_builds.insert(PID=None, BuildId=buildId, start_time=datetime.datetime.today())

# determine distro and therefore distro's .list file
listfile = DISTOLIST_PATH + platform.dist()[0].lower() + "_" + platform.dist()[1].lower() + '.list'
# print listfile

# create jail and copy src code into jail
subprocess.call([SCRIPT_FILE, JAIL_DIR, SRC_DIR + "main.py", listfile]);

p = subprocess.Popen(["chroot", JAIL_DIR, "python", USER_SCRIPT_PATH], stdout=PIPE, stderr=PIPE)

# update the buid in the database (for the scheduler)
db(db.current_builds.BuildId == buildId).update(PID=p.pid, start_time=datetime.datetime.today())
db.commit()

# wait until the build has finished
p.wait()

# update the database and distribute output
db(db.current_builds.PID==p.pid).update(output=p.stdout.read(), error=p.stderr.read(), finished=True)

file.write(p.stdout.read());

file.close()



