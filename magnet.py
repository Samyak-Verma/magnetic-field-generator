import pyvisa as visa
import os
import time
import csv
from datetime import datetime
from Common.CSVWriter import CSVWriter
from Common.Observable import Observable
from Common.Settings import Settings
from Common.VISAMachine import PowerSupply, VoltageNanovoltmeter, CurrentSource
from Common.Spans import span

if os.path.exists('output') == False:
	os.mkdir('output')

def check_and_get_filename(SettingsHolder: Settings):	
	file_name = SettingsHolder.get("file_name")
	if(file_name == SettingsHolder.defaults["file_name"]):
		file_name = f"output-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
		print(f"We are loading a default file name from TOML, using a safety feature to avoid this. Will save as {file_name}")

	return f"{SettingsHolder.get("file_directory")}/{file_name}"

def setup_machines(SettingsHolder: Settings):
	rm = visa.ResourceManager()
	try:
		Nanovoltmeter = VoltageNanovoltmeter(
			'GPIB0::8::INSTR',
			rm,
			voltmeter_range = SettingsHolder.get("nanovoltmeter_range"),
		)
		KeithleySource = CurrentSource(
			'GPIB0::10::INSTR',
			rm,
			amperage = SettingsHolder.get("currentsource_amperage"),
			compliance = SettingsHolder.get("currentsource_compliance"),
		)
		KEPCO = PowerSupply(
			'GPIB0::6::INSTR',
			rm,
			voltage = SettingsHolder.get("powersupply_voltage_compliance"),
			current = SettingsHolder.get("powersupply_current"),
		)
	except visa.VisaIOError as e:
		print(f"Could not connect to one of the machines. Please check your connections. {e}")
		return
	
	return {
		"Power Supply": KEPCO,
		"Voltage Nanovoltmeter": Nanovoltmeter,
		"Current Source": KeithleySource,
	}

class DataCollector(Observable):
	def __init__(self, machines_dict, filename, SettingsHolder: Settings):
		super().__init__()
		self.nanovoltmeter = machines_dict["Voltage Nanovoltmeter"]
		self.wait_time = SettingsHolder.get("milliseconds_between_measurements") / 1000
		self.Supply: PowerSupply = machines_dict["Power Supply"]
		self.Source: CurrentSource = machines_dict["Current Source"]
		self.filename = filename
		self.CSV = CSVWriter(
			file_path = filename,
			power_amperage = self.Supply.current,
			power_voltage = self.Supply.voltage,
			current_source_amperage = self.Source.amperage,
		)

		# modified on runtime
		self.start_time = 0
		self.time_to_initialize = 0
		self.number_of_runs = 0
		self.current_stage = 0

	def collect_data_infinite(self):
		self.start_time = time.time()
		while True:
			if(self.number_of_runs is not 0 and self.number_of_runs % 10 is 0 and self.current_stage >= 5):
				self.increment_stage()

			time.sleep(self.wait_time)
			time.sleep(1) # delete me later thanks

			self.nanovoltmeter.prepare_for_results()

			read_voltage = self.nanovoltmeter.get_results()
			if self.time_to_initialize == 0: # important to have this so data looks clean
				self.time_to_initialize = time.time() - self.start_time

			raw_time_of_measurement = round((time.time() - self.start_time) - self.time_to_initialize, ndigits = 1) # we can be more precise in time measurement but it doesn't matter
			time_of_measurement = f'{raw_time_of_measurement:10.2f}'
	
			print(f"Voltage Read: {read_voltage}")
			results_dict = {
				"time": time_of_measurement,
				"stage_voltage": self.current_stage,
				"read_voltage": read_voltage,
			}
			self.CSV.write(results_dict)
			
			self.number_of_runs += 1

	def single_run(self):
		# What we do in "single run" is a task-specific operation for the intents of our experiment.
		# We will take the input from SettingsHolder and read the voltage once.
		# We will then set Magnet Current to 0, and read the voltage again.
		self.start_time = time.time()
		self.nanovoltmeter.prepare_for_results()
		magnet_amperage_one = self.Source.amperage
		voltage_one = self.nanovoltmeter.get_results()
		self.time_to_initialize = time.time() - self.start_time
		time_one = round((time.time() - self.start_time) - self.time_to_initialize, ndigits = 1)
		print(span.blue(f"Voltage^1 Read: {voltage_one}"))

		print(f"Now turning the magnet current off.")
		self.Supply.disable_output()
		time.sleep(1) # let the magnet current pass a bit as a precaution
		self.nanovoltmeter.prepare_for_results()
		voltage_two = self.nanovoltmeter.get_results()
		time_two = round((time.time() - self.start_time) - self.time_to_initialize, ndigits = 1)
		print(span.blue(f"Voltage^2 Read: {voltage_two}"))

		print(span.green(f"deltaVoltage: {voltage_two - voltage_one}"))

		#write resutls to CSV
		with open(self.filename, 'a', newline='') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(["Time", "Current Amperage", "Voltage"])
			writer.writerow([time_one, magnet_amperage_one, voltage_one])
			writer.writerow([time_two, 0, voltage_two])

	def increment_stage(self):
		self.current_stage += 1
		# self.Supply.write("whatever")
		return


def standard_operation(SettingsHolder):
	file_name = check_and_get_filename(SettingsHolder)
	machines_dict = setup_machines(SettingsHolder)

	data_collector = DataCollector(machines_dict, file_name, SettingsHolder)
	data_collector.single_run()
	# data_collector.collect_data_infinite()

	for thing in machines_dict:
		machines_dict[thing].close()

def CLI_input(SettingsHolder: Settings):
	SettingsHolder.set("powersupply_current", float(input("Enter the current for the magnet. (A): ")))
	SettingsHolder.set("currentsource_amperage", float(input("Enter the amperage for the current source (sample). (A): ")))

def main():
	SettingsHolder = Settings()

	if SettingsHolder.using_toml() is False:
		CLI_input(SettingsHolder)

	standard_operation(SettingsHolder)


if __name__ == "__main__":
	main()
