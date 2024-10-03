from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundPDCIPForNetBIOSGroup(AbstractFilteredObject):
	def __init__(self, path:dict, group:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		self.info['netbios_group'] = group
		self.info['ip'] = ip

	def display(self):
		return f"Found PDC role for NetBIOS group ({self.info['netbios_group']}) for ip ({self.info['ip']})"


	def captured(self) -> dict:
		return self.info

	def get_netbios_group(self):
		return self.info['netbios_group']

	def get_path(self):
		return self.info['path']

	def get_ip(self):
		return self.info['ip']