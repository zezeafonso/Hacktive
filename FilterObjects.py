from AbstractClasses import AbstractFilteredObject



class Filtered_NewInterface(AbstractFilteredObject):
	def __init__(self, path:dict, interface:str):
		self.info = dict()
		self.info['path'] = path
		self.info['interface'] = interface

	def captured(self) -> dict:
		return self.info

	def get_interface(self):
		return self.info['interface']

	def get_path(self):
		return self.info['path']


class Filtered_NewNetworkForInterface(AbstractFilteredObject):
	def __init__(self, network:str, interface:str):
		self.info = dict()
		self.info['interface'] = interface
		self.info['network'] = network

	def captured(self) -> dict:
		return self.info

	def get_interface(self):
		return self.info['interface']

	def get_network(self):
		return self.info['network']


class Filtered_FoundOurIPForNetwork(AbstractFilteredObject):
	def __init__(self, interface:str, network:str, ip:str):
		self.info = dict()
		self.info['interface'] = interface
		self.info['network'] = network
		self.info['ip'] = ip

	def captured(self) -> dict:
		return self.info

	def get_ip(self):
		return self.info['ip']

	def get_interface(self):
		return self.info['interface']

	def get_network(self):
		return self.info['network']


class Filtered_FoundNetBIOSHostnameWithSMB(AbstractFilteredObject):
	def __init__(self, path, hostname:str):
		self.info = dict()
		self.info['path'] = path
		if hostname is not None:
			self.info['netbios_hostname'] = hostname

	def captured(self) -> dict:
		return self.info

	def get_hostname(self):
		return self.info['netbios_hostname']

	def get_path(self):
		return self.info['path']


class Filtered_FoundNetBIOSGroupForIP(AbstractFilteredObject):
	def __init__(self, path:dict, group:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		self.info['netbios_group'] = group
		self.info['ip'] = ip

	def captured(self) -> dict:
		return self.info

	def get_netbios_group(self):
		return self.info['netbios_group']

	def get_path(self):
		return self.info['path']

	def get_ip(self):
		return self.info['ip']


class Filtered_FoundPDCIPForNetBIOSGroup(AbstractFilteredObject):
	def __init__(self, path:dict, group:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		self.info['netbios_group'] = group
		self.info['ip'] = ip

	def captured(self) -> dict:
		return self.info

	def get_netbios_group(self):
		return self.info['netbios_group']

	def get_path(self):
		return self.info['path']

	def get_ip(self):
		return self.info['ip']


class Filtered_FoundNetBIOSHostnameForIP(AbstractFilteredObject):
	def __init__(self, path:dict, hostname:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		self.info['netbios_hostname'] = hostname
		self.info['ip'] = ip

	def captured(self) -> dict:
		return self.info

	def get_hostname(self):
		return self.info['netbios_hostname']

	def get_path(self):
		return self.info['path']

	def get_ip(self):
		return self.info['ip']



class Filtered_NewIPForNetwork(AbstractFilteredObject):
	def __init__(self, path:list, ip:str):
		self.info = dict()
		self.info['path'] = path
		if ip is not None:
			self.info['ip'] = ip

	def captured(self) -> dict:
		return self.info

	def get_ip(self):
		return self.info['ip']

	def get_path(self):
		return self.info['path']
	
