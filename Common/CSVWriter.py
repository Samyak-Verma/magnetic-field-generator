import csv
import os
from decimal import Decimal

class CSVWriter(object):
	def __init__(self, file_path, power_amperage, power_voltage, current_source_amperage):
		self.file_path = file_path
		self.power_amperage = power_amperage
		self.power_voltage = power_voltage
		self.current_source_amperage = current_source_amperage
		self.setup_csv_file()
	
	def setup_csv_file(self):
		# each entry is written left-to-right horizontally in order
		file_header = [
			"Time (seconds)",
			"Stage Voltage - Power Supply (V)"
			"Read Voltage - Nanovoltmeter (V)",
			f"Power Supply Amperage (A): {'%.2E' % Decimal(self.power_amperage)}"
			f"Power Supply Voltage (V): {'%.2E' % Decimal(self.power_voltage)}"
			f"Current Source Amperage (A): {'%.2E' % Decimal(self.current_source_amperage)}"
		]

		with open(self.file_path, 'w', newline='') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(file_header)
	
	def write(self, result_dict):
		with open(self.file_path, 'a', newline='') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow([result_dict["time"], result_dict["stage_voltage"], result_dict["read_voltage"]])