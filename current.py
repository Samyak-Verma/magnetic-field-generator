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

	rm = visa.ResourceManager()
	KEPCO = PowerSupply('GPIB0::6::INSTR', rm, voltage = 20, current = 0.5) # sets up the current and sets it to the needed mode
	Nanovoltmeter = VoltageNanovoltmeter('GPIB0::7::INSTR', rm, voltmeter_range = 0.1)
	KeithleySource = CurrentSource('GPIB0::8::INSTR', rm)

	# record_data_in_excel(user_current, file_name)

	KEPCO.close()

if __name__ == "__main__":
	main()
