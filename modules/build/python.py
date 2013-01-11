GRADING_FILE = '/grades.grd'

def binary():
	return 'python'

def getInvokeCommand(path):
	return  [binary(), path]

def buildAssertion(function_name, arguments, expected_result):
	output = '\t	assert ' + function_name + '( ' + arguments + ' )' + ' == ' + expected_result + '\r\n'
	return output;

def buildPointSet(id, assertions):
	output =  'try:' + '\r\n'

	output += '\r\n'.join(assertions)

	#output += '\t	assert ' + function_name + '( ' + arguments + ' )' + ' == ' + expected_result + '\r\n'
	output +=  'except Exception, e:' + '\r\n'
	output += '\t	print "failed"' + '\r\n'
	output += '\t	rating.write("' + str(id) + ':0\\r\\n")' + '\r\n'
	output +=  'else:' + '\r\n'
	output += '\t	print "passed"' + '\r\n'
	output += '\t	rating.write("' + str(id) + ':1\\r\\n")' + '\r\n'
	return output;

def buildTests(points):
	output =  'rating = open(\'' + GRADING_FILE + '\', \'w\')\r\n'
	output += ''
	output += '\r\n'.join(points)
	output += 'rating.close()\r\n'
	return output