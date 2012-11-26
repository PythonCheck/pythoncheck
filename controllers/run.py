# coding: utf8
import subprocess

def submit():
	print "Hi. We will now run the test."

# user code is saved to database
# user code is run
# the output is caputured and replied
def run():
	src=request.vars.code;
	language=request.vars.language
	exercise=request.vars.exercise
	course=request.vars.course
	mode=None

	# check if we are developing for an exercise or just so
	if (language != None) & (exercise != None) & (course != None):

		highestRev=0

		# (db.code.language==language) & (db.code.exercise==exercise) & (db.code.course==course)
		for row in db((db.code.language==language) & (db.code.exercise==exercise) & (db.code.course==course)).select(db.code.version):
			if row.version > highestRev:
				highestRev=row.version
		print 'highestRev:', highestRev

		mode='submit'
		#db.code.insert()
	else:
		print 'test only!'
		mode='test'

	# run code
	"""
	# write src code into file
	file=open('/path/to/src/code', 'w')
	file.write(code)
	file.close()

	# create jail and copy src code into jail
	subprocess.call(["./create.sh", "/tmp/jail", "/path/to/scr/code"]);

	# enter jail
	p = subprocess.Popen(["chroot", "/tmp/jail", "python", "/path/to/user/script"], stdout=PIPE)
	#TODO register in global process table for scheduler

	# wait for output
	p.wait()

	# capture output and prepare for printing
	"""

	return dict(output="this is an output string", error="this is an error", mode=mode)
