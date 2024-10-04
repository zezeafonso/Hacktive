from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundNewIPForNetwork(AbstractFilteredObject):
	def __init__(self, path:list, ip:str):
		self.info = dict()
		self.info['path'] = path
		if ip is not None:
			self.info['ip'] = ip

	def display(self):
		return f"Found live host ip ({self.info['ip']}) for network"


	def captured(self) -> dict:
		return self.info

	def get_ip(self):
		return self.info['ip']

	def get_path(self):
		return self.info['path']