import csv
import os
from decimal import Decimal

class CSVWriter(object):
	def __init__(self, filepath_holder, read_amperage, comment):
		self.filepath_holder = filepath_holder
		self.read_amperage = read_amperage
		self.comment = comment
		self.file_path = None
		self.setup_csv_file()
	
	def setup_csv_file(self):
		self.file_path = self.filepath_holder.get_file_path()
		# each entry is written left-to-right horizontally in order
		file_header = [
			"Time (seconds)",
			"Voltage (V)",
			"Resistances (Ohms)",
			"Temperature (Celsius)",
			f"Amperage: {'%.2E' % Decimal(self.read_amperage)} A",
			f"Timestamp: {self.filepath_holder.get_timestamp()}",
			f"Comment: {self.comment}" if self.comment != "" else None,
		]

		with open(self.file_path, 'w', newline='') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(file_header)

		print(f"Will save results to {os.path.abspath(self.file_path)}")
	
	def write(self, result_dict):
		with open(self.file_path, 'a', newline='') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow([result_dict["time"], result_dict["voltage"], result_dict["resistance"], result_dict["temperature"]])