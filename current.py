import pyvisa as visa
import pandas as pd
import os
import openpyxl
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

def main():
	TOMLSettingsHolder = TOMLSettings()
	if TOMLSettingsHolder.using_toml() is False:
		print("You must set USE_TOML to true in MagneticFieldSettings.toml to use this script.")
		return
	
	toml_file_name = TOMLSettingsHolder.get("file_name")
	if(toml_file_name == TOMLSettingsHolder.defaults["file_name"]):
		toml_file_name = f"output-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
		print(f"We are loading a default file name from TOML, using a safety feature to avoid this. Will save as {toml_file_name}")
		return

	file_name = f"output/{toml_file_name}"
	rm = visa.ResourceManager()
	try:
		KEPCO = PowerSupply(
			'GPIB0::6::INSTR',
			rm,
			voltage = TOMLSettingsHolder.get("powersupply_voltage_compliance"),
			current = TOMLSettingsHolder.get("powersupply_current"),
		)
		Nanovoltmeter = VoltageNanovoltmeter(
			'GPIB0::8::INSTR',
			rm,
			voltmeter_range = TOMLSettingsHolder.get("nanovoltmeter_range"),
		)
		KeithleySource = CurrentSource(
			'GPIB0::10::INSTR',
			rm,
			amperage = TOMLSettingsHolder.get("currentsource_amperage"),
			compliance = TOMLSettingsHolder.get("currentsource_compliance"),
		)
	except visa.VisaIOError:
		print("Could not connect to one of the machines. Please check your connections.")
		return
	
	machines = [KEPCO, Nanovoltmeter, KeithleySource]

	# record_data_in_excel(user_current, file_name)

	for machine in machines:
		machine.close()

if __name__ == "__main__":
	main()
