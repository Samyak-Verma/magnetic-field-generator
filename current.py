import pyvisa as visa
import pandas as pd
import os
import openpyxl
from datetime import datetime
from Common.VISAMachine import PowerSupply

if os.path.exists('output') == False:
	os.mkdir('output')

def send_current_to_power_supply(current, power_supply):
	try:
		# Set current
		power_supply.write(f'CURR {current}')
		print(f"Current set to {current} A")

		# Optionally, read back the set value if necessary
		response = power_supply.query('CURR?').rstrip()
		print(f"Current confirmed at: {response} A")
	except visa.VisaIOError as e:
		print(f"Error communicating with the power supply: {e}")
	except Exception as ex:
		print(f"An error occurred with the power supply: {ex}")

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
	cli_current = input("Enter the current value to set (in A): ")
	if cli_current != "":
		user_current = float(cli_current)
	return file_name, user_current

def main():
	user_inputs = get_variables()
	file_name = user_inputs[0]
	user_current = user_inputs[1]

	rm = visa.ResourceManager()
	KEPCO = PowerSupply('GPIB0::6::INSTR', rm, user_current)

	send_current_to_power_supply(user_current, KEPCO)
	record_data_in_excel(user_current, file_name)

	KEPCO.close()

if __name__ == "__main__":
	main()
