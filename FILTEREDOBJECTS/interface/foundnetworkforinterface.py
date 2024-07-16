from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_NewNetworkForInterface(AbstractFilteredObject):
	def __init__(self, network:str, interface:str):
		self.info = dict()
		self.info['interface_name'] = interface
		self.info['network_address'] = network

	def display(self):
		return f" network ({self.info['network_address']}) for interface ({self.info['interface_name']})"

	def captured(self) -> dict:
		return self.info

	def get_interface_name(self):
		return self.info['interface_name']

	def get_network_address(self):
		return self.info['network_address']