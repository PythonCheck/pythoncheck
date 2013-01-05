from gluon.scheduler import Scheduler
from datetime import datetime, timedelta
from signal import SIGKILL
import os

def build_monitor(): 
	running_builds = db((db.current_builds.finished==False)).select()
	for build in running_builds:
		# check which of the running builds are running too long
		if (build.start_time + timedelta(seconds=MAX_BUILD_TIME)) < datetime.now():
			if build.PID == None:
				print 'The build with the ', build.id, 'has not started yet but has already timed out. It is probably garbage.'
			else:
				# kill the build. the build module will resume and take care of cleanup, etc.
				print 'The build', build.id, 'has timed out!'
				os.kill(build.PID, SIGKILL)

	return True

TASK_UUID = '29aa3d33-1f7b-4d11-a589-75afa399a4e9'

# initiate scheduler
scheduler = Scheduler(db, discard_results=False, heartbeat=1)


# build_monitor task - drop and reinsert to avoid time stamp conflicts
scheduler.queue_task('build_monitor', task_name='build_monitor', repeats=0, period=2, timeout=2, uuid=TASK_UUID, retry_failed=-1)
