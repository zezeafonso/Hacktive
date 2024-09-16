from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundNetBIOSHostnameForIP(AbstractFilteredObject):
	def __init__(self, path:dict, hostname:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		self.info['netbios_hostname'] = hostname
		self.info['ip'] = ip

	def display(self):
		return f" netbios hostname ({self.info['netbios_hostname']}) for ip ({self.info['ip']})"


	def captured(self) -> dict:
		return self.info

	def get_hostname(self):
		return self.info['netbios_hostname']

	def get_path(self):
		return self.info['path']

	def get_ip(self):
		return self.info['ip']

