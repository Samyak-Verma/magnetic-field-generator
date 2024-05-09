import pyvisa as visa
import pandas as pd
import os
import openpyxl
import time
from datetime import datetime
from Common.TOMLSettings import TOMLSettings
from Common.VISAMachine import PowerSupply, VoltageNanovoltmeter, CurrentSource

if os.path.exists('output') == False:
	os.mkdir('output')

def record_data_in_excel(current, file_name):
	try:
		data = pd.read_excel(file_name, index_col=0)
	except FileNotFoundError:
		data = pd.DataFrame(columns=['Time', 'Current (A)'])

	new_data = pd.DataFrame({
		'Time': [datetime.now()],
		'Current (A)': [current],
	})

	data = pd.concat([data, new_data], ignore_index=True)
	data.to_excel(file_name)
	print(f"Data recorded in {file_name}")

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
		KEPCO = PowerSupply(
			'GPIB0::6::INSTR',
			rm,
			voltage = SettingsHolder.get("powersupply_voltage_compliance"),
			current = SettingsHolder.get("powersupply_current"),
		)
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
	except visa.VisaIOError as e:
		print(f"Could not connect to one of the machines. Please check your connections. {e}")
		return
	
	return {
		"Power Supply": KEPCO,
		"Voltage Nanovoltmeter": Nanovoltmeter,
		"Current Source": KeithleySource,
	}

def collect_data(machines_dict, milliseconds_between_measurements):
	returnable_results = []
	nanovoltmeter = machines_dict["Voltage Nanovoltmeter"]
	while True:
		time.wait(milliseconds_between_measurements / 1000)


def main():
	TOMLSettingsHolder = TOMLSettings()

	file_name = check_and_get_filename(TOMLSettingsHolder)
	machines_dict = setup_machines()

	results = collect_data(machines_dict, TOMLSettingsHolder.get("milliseconds_between_measurements"))

	# record_data_in_excel(user_current, file_name)

	for thing in machines_dict:
		machines_dict[thing].close()

if __name__ == "__main__":
	main()
