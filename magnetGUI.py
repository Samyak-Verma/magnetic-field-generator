from magnet import standard_operation
from Common.Settings import Settings
from Common.InputField import InputField, InputType
import dearpygui.dearpygui as dpg
import os

SettingsHolder = Settings()

def send_information():
	print("Sending Information")

	for field in input_fields:
		field_tag = field.get_tag()
		field_value = field.get_value()
		print(f"Setting {field_tag} to {field.get_value()}")
		SettingsHolder.set(field_tag, field_value)

	# result = standard_operation(SettingsHolder)
	# print(result)

def create_inputs():
	global input_fields
	input_fields = []
	dpg.add_text("Change the values below to change the settings for the magnet.")
	dpg.add_text("The following do not need to be changed very often, but are presented if you need.")
	
	input_fields.append(InputField("File Directory", "file_directory", InputType.STRING, SettingsHolder))
	input_fields.append(InputField("File Name", "file_name", InputType.STRING, SettingsHolder))
	input_fields.append(InputField("Magnet Voltage Compliance", "powersupply_voltage_compliance", InputType.INT, SettingsHolder))
	input_fields.append(InputField("Current Source Compliance", "currentsource_compliance", InputType.INT, SettingsHolder))
	input_fields.append(InputField("Nanovoltmeter Range", "nanovoltmeter_range", InputType.INT, SettingsHolder))
	input_fields.append(InputField("Milliseconds Between Measurements", "milliseconds_between_measurements", InputType.INT, SettingsHolder))

	dpg.add_text("\n\nThe following are what you really tend to need for experimentation.")
	input_fields.append(InputField("Current Source Amperage", "currentsource_amperage", InputType.INT, SettingsHolder))
	input_fields.append(InputField("Magnet Current Amperage", "powersupply_current", InputType.INT, SettingsHolder))
	dpg.add_button(label = "Submit", callback = send_information)

	dpg.add_text("\n\n\n")
	dpg.add_text(label = "Information", tag = "Information", default_value = "Awaiting Send...")

dpg.create_context()
dpg.create_viewport(title = "Resistance Tester")
dpg.setup_dearpygui()

with dpg.window(label="Main Window", tag = "Main Window", autosize = True, no_close = True):
	create_inputs()

dpg.maximize_viewport()
dpg.set_primary_window("Main Window", True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()