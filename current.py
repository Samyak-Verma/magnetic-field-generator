import pyvisa as visa
import pandas as pd
import os
from datetime import datetime
from Common.VISAMachine import Nanovoltmeter, PowerSupply

if os.path.exists('output') == False:
	os.mkdir('output')

def send_current_to_power_supply(current, power_supply):
	try:
		# Set current
		power_supply.write(f'CURR {current}')
		print(f"Current set to {current} A")

		# Optionally, read back the set value if necessary
		response = power_supply.query('CURR?')
		print(f"Current confirmed at: {response} A")
	except visa.VisaIOError as e:
		print(f"Error communicating with the power supply: {e}")
	except Exception as ex:
		print(f"An error occurred with the power supply: {ex}")

def read_voltage_from_nanovoltmeter(nanovoltmeter):
	try:
		voltage = nanovoltmeter.query('READ?')
		print(f"Voltage read as: {voltage} V")
		return voltage
	except visa.VisaIOError as e:
		print(f"Error communicating with the nanovoltmeter: {e}")
	except Exception as ex:
		print(f"An error occurred with the nanovoltmeter: {ex}")

def record_data_in_excel(current, voltage, file_name):
	try:
		data = pd.read_excel(file_name, index_col=0)
	except FileNotFoundError:
		data = pd.DataFrame(columns=['Time', 'Current (A)', 'Voltage (V)'])

	new_data = pd.DataFrame({
		'Time': [datetime.now()],
		'Current (A)': [current],
		'Voltage (V)': [voltage]
	})

	data = pd.concat([data, new_data], ignore_index=True)
	data.to_excel(file_name)
	print(f"Data recorded in {file_name}")

def main():
	rm = visa.ResourceManager()

	input_file_name = ""
	input_file_name = input("Enter the name of the Excel file to save data (include .xlsx): ")
	if input_file_name == "":
		input_file_name = "data.xlsx"
	file_name = f"output/{input_file_name}"
	user_current = 0.1
	cli_current = input("Enter the current value to set (in A): ")
	if cli_current != "":
		user_current = float(cli_current)

	KEPCO = PowerSupply('GPIB0::6::INSTR', rm, user_current)
	Keithley = Nanovoltmeter('GPIB0::5::INSTR', rm)

	send_current_to_power_supply(user_current, KEPCO)
	voltage = read_voltage_from_nanovoltmeter(Keithley)
	record_data_in_excel(user_current, voltage, file_name)

	KEPCO.close()
	Keithley.close()

if __name__ == "__main__":
	main()
