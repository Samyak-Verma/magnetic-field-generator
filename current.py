import pyvisa as visa
import os
import time
from datetime import datetime
from Common.CSVWriter import CSVWriter
from Common.Observable import Observable
from Common.TOMLSettings import TOMLSettings
from Common.VISAMachine import PowerSupply, VoltageNanovoltmeter, CurrentSource

if os.path.exists('output') == False:
	os.mkdir('output')

def check_and_get_filename(SettingsHolder: TOMLSettings):
	if SettingsHolder.using_toml() is False:
		print("You must set USE_TOML to true in MagneticFieldSettings.toml to use this script.")
		return
	
	toml_file_name = SettingsHolder.get("file_name")
	if(toml_file_name == SettingsHolder.defaults["file_name"]):
		toml_file_name = f"output-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
		print(f"We are loading a default file name from TOML, using a safety feature to avoid this. Will save as {toml_file_name}")

def setup_machines(SettingsHolder: TOMLSettings):
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
	def __init__(self, machines_dict, filename, TOMLSettingsHolder: TOMLSettings):
		super().__init__()
		self.nanovoltmeter = machines_dict["Voltage Nanovoltmeter"]
		self.wait_time = TOMLSettingsHolder.get("milliseconds_between_measurements") / 1000
		Supply: PowerSupply = machines_dict["Power Supply"]
		Source: CurrentSource = machines_dict["Current Source"]
		self.CSV = CSVWriter(
			file_path = filename,
			power_amperage = Supply.current,
			power_voltage = Supply.voltage,
			current_source_amperage = Source.amperage,
		)

		# modified on runtime
		self.start_time = 0
		self.time_to_initialize = 0

	def collect_data(self):
		self.start_time = time.time()
		while True:
			time.sleep(self.wait_time)
			time.sleep(1) # delete me later thanks

			self.nanovoltmeter.prepare_for_results()

			read_voltage = self.nanovoltmeter.get_results()
			if self.time_to_initialize == 0: # important to have this so data looks clean
				self.time_to_initialize = time.time() - self.start_time

			raw_time_of_measurement = round((time.time() - self.start_time) - self.time_to_initialize, ndigits = 1) # we can be more precise in time measurement but it doesn't matter
			time_of_measurement = f'{raw_time_of_measurement:10.2f}'
	
			print(read_voltage)
			results_dict = {
				"time": time_of_measurement,
				"stage_voltage": 0,
				"read_voltage": read_voltage,
			}
			self.CSV.write(results_dict)


def main():
	TOMLSettingsHolder = TOMLSettings()

	file_name = check_and_get_filename(TOMLSettingsHolder)
	machines_dict = setup_machines(TOMLSettingsHolder)

	data_collector = DataCollector(machines_dict, file_name, TOMLSettingsHolder)
	data_collector.collect_data()

	# record_data_in_excel(user_current, file_name)

	for thing in machines_dict:
		machines_dict[thing].close()

if __name__ == "__main__":
	main()
