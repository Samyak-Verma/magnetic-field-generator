import time

class FilePath(object):
	def __init__(self, file_directory):
		self.file_path = None
		self.timestamp = None
		
		self.file_directory = file_directory

	def get_file_path(self, regenerate = True):
		if regenerate is True or self.file_path is None:
			self.timestamp = time.strftime("%Y%m%d-%H%M%S")
			file_name = f"ResistanceTester-{self.timestamp}.csv"
			self.file_path = f"{self.file_directory}/{file_name}"

		return self.file_path
	
	def get_timestamp(self):
		if self.file_path is None:
			self.get_file_path()

		return self.timestamp