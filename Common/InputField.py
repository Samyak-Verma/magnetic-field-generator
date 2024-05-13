import dearpygui.dearpygui as dpg
from enum import Enum
from Common.Settings import Settings

class InputType(Enum):
	INT = 0
	FLOAT = 1
	STRING = 2

class InputField:
	def __init__(self, name, type, SettingsHolder, width = 100, tooltip = None):
		self.SettingsHolder: Settings = SettingsHolder
		self.type: InputType = type
		self.label = name
		self.tag = name
		self.default_value = self.SettingsHolder.get(name)
		self.width = width
		self.tooltip = tooltip

		self.create_input()

	def create_input(self):
		if self.type is InputType.INT:
			dpg.add_input_int(tag = self.tag, width = self.width, default_value = self.default_value)
		elif self.type is InputType.FLOAT:
			dpg.add_input_float(tag = self.tag, width = self.width, default_value = self.default_value)
		elif self.type is InputType.STRING:
			dpg.add_input_text(tag = self.tag, width = self.width, default_value = self.default_value)

	def get_tag(self):
		return self.tag

	def get_value(self):
		return dpg.get_value(self.tag)

