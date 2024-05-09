import pyvisa as visa
import time

class VisaMachine(object):
	def __init__(self, name, visa_address, RM):
		self.name = name
		self.visa_address = visa_address
		self.RM: visa.ResourceManager = RM

		self.resource: visa.Resource = None
		self.timeout = 5000 #milliseconds

		self.initialize()

	def initialize(self):
		intializing_machine = self.base_connection()
		self.additional_setup(intializing_machine)
		self.resource = intializing_machine

	def base_connection(self):
		print(f"Initializing {self.name} at {self.visa_address}")
		intializing_machine = self.RM.open_resource(self.visa_address)
		intializing_machine.timeout = self.timeout
		return intializing_machine
	
	def write(self, command):
		return self.resource.write(command)

	def query(self, command):
		return self.resource.query(command)

	def additional_setup(self, machine):
		return
	
	def pre_close(self):
		return

	def close(self):
		self.pre_close()
		print(f"Closing out the {self.name} at {self.visa_address}.")
		self.resource.close()
	
class CurrentSource(VisaMachine):
	def __init__(self, visa_address, RM, amperage, compliance):
		self.amperage = amperage
		self.compliance = compliance
		super().__init__("Current Source", visa_address, RM)

	def additional_setup(self, machine):
		super().additional_setup(machine)
		machine.write("*RST")
		machine.write(":SOUR:CLEAR")
		machine.write(":SOUR:CURR:RANG:AUTO ON")
		machine.write(f":SOUR:CURR:COMP {self.compliance}")
		validated_compliance = f"{machine.query(":SOUR:CURR:COMP?")}".rstrip()
		print(f"Current Source is set to {float(validated_compliance):.2f} V compliance")

		machine.write(f":SOUR:CURR {self.amperage:.9f}")
		machine.write(":OUTP ON")
		validated_output = f"{machine.query(":SOUR:CURR:AMPL?")}".rstrip()
		self.amperage = float(validated_output)
		print(f"Current Source is outputting {validated_output} A")
		time.sleep(1) # let amperage pass a bit as a precaution

	def pre_close(self):
		# self.write(":OUTP OFF") works but is annoying for the time being
		return super().pre_close()

class Nanovoltmeter(VisaMachine):
	def __init__(self, name, visa_address, RM):
		super().__init__(name, visa_address, RM)

	def prepare_for_results(self):
		self.write(":INIT")

	def get_results(self):
		self.query("*OPC?")
		return float(self.query(":FETC?"))

	def additional_setup(self, machine):
		machine.write(":STAT:OPER:ENAB 1")
		return super().additional_setup(machine)

class VoltageNanovoltmeter(Nanovoltmeter):
	def __init__(self, visa_address, RM, voltmeter_range):
		self.voltmeter_range = voltmeter_range
		super().__init__("Voltage Nanovoltmeter", visa_address, RM)

	def additional_setup(self, machine):
		machine.write("*RST")
		machine.write(":CONF:VOLT")
		machine.write(f":VOLT:RANG {self.voltmeter_range}")
		return super().additional_setup(machine)

class TemperatureNanovoltmeter(Nanovoltmeter):
	def __init__(self, visa_address, RM):
		super().__init__("Temperature Nanovoltmeter", visa_address, RM)

	def additional_setup(self, machine):
		machine.write("*RST")
		machine.write(":CONF:TEMP")
		machine.write(":SENS:TEMP:DIG 7")
		return super().additional_setup(machine)

class PowerSupply(VisaMachine):
	def __init__(self, visa_address, RM, current):
		self.current = current
		super().__init__("Power Supply", visa_address, RM)

	def additional_setup(self, machine):
		super().additional_setup(machine)
		machine.write("*RST")
		machine.write(f'CURR {self.current}')
		response = machine.query('CURR?').rstrip()
		print(f"Current confirmed at: {response} A")