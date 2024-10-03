from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundNewInterface(AbstractFilteredObject):
	def __init__(self, path:dict, interface:str):
		self.info = dict()
		self.info['path'] = path
		self.info['interface_name'] = interface

	def display(self):
		return f"Found interface ({self.info['interface_name']})"	

	def captured(self) -> dict:
		return self.info

	def get_interface_name(self):
		return self.info['interface_name']

	def get_path(self):
		return self.info['path']