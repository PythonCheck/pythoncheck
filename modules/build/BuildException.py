class BuildException(Exception):
	def __init__(self, stdout, stderr, exceptionDescription):
		self.stdout = stdout
		self.stderr = stderr
		self.exceptionDescription = exceptionDescription

	def __str__(self):
		return self.exceptionDescription
