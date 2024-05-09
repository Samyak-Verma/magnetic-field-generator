import pyvisa as visa
import pandas as pd
import os
import openpyxl
from datetime import datetime
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

def get_variables():
	input_file_name = input("Enter the name of the Excel file to save data (include .xlsx): ")
	if input_file_name == "":
		input_file_name = "data.xlsx"
	file_name = f"output/{input_file_name}"

	user_current = 0.1
	cli_current = input("Enter the Power Supply current value to set (in A): ")
	if cli_current != "":
		user_current = float(cli_current)

	
	return file_name, user_current

def main():
	# user_inputs = get_variables()
	# file_name = user_inputs[0]
	# user_current = user_inputs[1]

	rm = visa.ResourceManager()
	KEPCO = PowerSupply('GPIB0::6::INSTR', rm, voltage = 20, current = 0.5) # sets up the current and sets it to the needed mode
	Nanovoltmeter = VoltageNanovoltmeter('GPIB0::7::INSTR', rm, voltmeter_range = 0.1)
	KeithleySource = CurrentSource('GPIB0::8::INSTR', rm)

	# record_data_in_excel(user_current, file_name)

	KEPCO.close()

if __name__ == "__main__":
	main()
