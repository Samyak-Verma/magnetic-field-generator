import toml
import os

class TOMLSettings(object):
	def __init__(self):
		self.toml_path = "./ResistanceTesterSettings.toml"
		# Edit these defaults as needed
		self.defaults = dict({
			"amperage": 1e-6,
			"comment": "",
			"compliance": 10,
			"default_number_of_entries": 150,
			"GPIB_current_source_integer": 10,
			"GPIB_nanovoltmeter_integer_temperature": 8,
			"GPIB_nanovoltmeter_integer_voltage": 5,
			"infinite_mode": False,
			"milliseconds_between_measurements": 0,
			"voltmeter_range": 10,
			"file_directory": "./ResistanceTesterData",
		})
		self.settings = None

		if not os.path.exists(self.toml_path):
			self.generate_toml()

		self.load_toml()

	def generate_toml(self):
		with open(self.toml_path, "w") as file:
			file.write("# !!IMPORTANT!! You must set USE_TOML to true to use any of the settings you update below.")
			file.write("\nUSE_TOML = false\n\n")
			toml.dump(self.defaults, file)

	def load_toml(self):
		with open(self.toml_path, "r") as file:
			read_settings = toml.load(file)
			if read_settings["USE_TOML"] is True: # we assume the user willfully left this as false, we notify them via the CLI what we're reading from anyways
				self.settings = read_settings

		self.create_file_directory()

	def create_file_directory(self):
		file_directory = None
		if self.using_toml() is True:
			file_directory = self.settings["file_directory"]
		else:
			file_directory = self.defaults["file_directory"]

		if not os.path.exists(file_directory):
			os.makedirs(file_directory)

	def using_toml(self):
		if self.settings is None:
			return False

		return True

	def get(self, key):
		if self.using_toml() is False:
			return self.defaults[key]

		return self.settings[key]
	
# we want to set up the toml file if it doesn't exist when the user installs the dependencies via the BAT file but not when we import this
if __name__ == "__main__":
	TOMLSettings()
