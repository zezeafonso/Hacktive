from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundOurIPForNetwork(AbstractFilteredObject):
	def __init__(self, interface:str, network:str, ip:str):
		self.info = dict()
		self.info['interface_name'] = interface
		self.info['network_address'] = network
		self.info['ip'] = ip

	def display(self):
		return f" our ip ({self.info['ip']}) for network ({self.info['network_address']}) for interface ({self.info['interface_name']})"

	def captured(self) -> dict:
		return self.info

	def get_ip(self):
		return self.info['ip']

	def get_interface_name(self):
		return self.info['interface_name']

	def get_network_address(self):
		return self.info['network_address']