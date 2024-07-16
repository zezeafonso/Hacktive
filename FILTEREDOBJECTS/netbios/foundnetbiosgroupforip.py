from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundNetBIOSGroupForIP(AbstractFilteredObject):
	def __init__(self, path:dict, group:str, _type:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		self.info['netbios_group'] = group
		self.info['group_type'] = _type
		self.info['ip'] = ip

	def display(self):
		return f"netbios group ({self.info['netbios_group']}#{self.info['group_type']}) for ip ({self.info['ip']})"


	def captured(self) -> dict:
		return self.info

	def get_netbios_group(self):
		return self.info['netbios_group']

	def get_path(self):
		return self.info['path']

	def get_ip(self):
		return self.info['ip']

	def get_type(self):
		return self.info['group_type']