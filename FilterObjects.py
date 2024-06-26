from AbstractClasses import AbstractFilteredObject



# ldap 

class Filtered_DomainComponentsFromLDAPQuery(AbstractFilteredObject):
	def __init__(self, path:dict, list_dc:list):
		self.info = dict()
		self.info['path'] = path

		# create the path ex: foxriver.local
		domain_components_path = ''
		for dc in list_dc:
			domain_components_path += dc + '.'
		domain_components_path = domain_components_path[:-1] # remove the final dot
		
		self.info['dc_path'] = domain_components_path

	def display(self):
		return f"Domain Components Path ({self.info['dc_path']}) from ldap query to ..."

	def captured(self) -> dict:
		return self.info

	def get_dc_path(self):
		return self.info['dc_path']



# msrpc 

class Filtered_FoundDomainTrust(AbstractFilteredObject):
	def __init__(self, domain_name:str):
		self.info = dict()
		self.info['domain_name'] = domain_name

	def display(self):
		return f"new domain trust for domain ({self.get_domain_name()})"

	def get_domain_name(self):
		return self.info['domain_name']

	def captured(self) -> dict:
		return self.info

# list interfaces

class Filtered_NewInterface(AbstractFilteredObject):
	def __init__(self, path:dict, interface:str):
		self.info = dict()
		self.info['path'] = path
		self.info['interface'] = interface

	def display(self):
		return f" new interface ({self.info['interface']})"	

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

	def display(self):
		return f" network ({self.info['network']}) for interface ({self.info['interface']})"

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

	def display(self):
		return f" our ip ({self.info['ip']}) for network ({self.info['network']}) for interface ({self.info['interface']})"

	def captured(self) -> dict:
		return self.info

	def get_ip(self):
		return self.info['ip']

	def get_interface(self):
		return self.info['interface']

	def get_network(self):
		return self.info['network']


# NETBIOS

class Filtered_FoundNetBIOSHostnameWithSMB(AbstractFilteredObject):
	def __init__(self, path, hostname:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		if hostname is not None:
			self.info['netbios_hostname'] = hostname
		self.info['ip'] = ip

	def display(self):
		return f" SMB server with netbios hostname ({self.info['netbios_hostname']}) for ip ({self.info['ip']})"

	def captured(self) -> dict:
		return self.info

	def get_hostname(self):
		return self.info['netbios_hostname']

	def get_path(self):
		return self.info['path']

	def get_ip(self):
		return self.info['ip']


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


class Filtered_FoundPDCIPForNetBIOSGroup(AbstractFilteredObject):
	def __init__(self, path:dict, group:str, ip:str):
		self.info = dict()
		self.info['path'] = path
		self.info['netbios_group'] = group
		self.info['ip'] = ip

	def display(self):
		return f" PDC role for netbios group ({self.info['netbios_group']}) for ip ({self.info['ip']})"


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



# ARP SCAN

class Filtered_NewIPForNetwork(AbstractFilteredObject):
	def __init__(self, path:list, ip:str):
		self.info = dict()
		self.info['path'] = path
		if ip is not None:
			self.info['ip'] = ip

	def display(self):
		return f" ip ({self.info['ip']}) for network"


	def captured(self) -> dict:
		return self.info

	def get_ip(self):
		return self.info['ip']

	def get_path(self):
		return self.info['path']




# PORTS AND SERVICES




class Filtered_SMBServiceIsUp(AbstractFilteredObject):
	def __init__(self, port:str):
		self.port = port

	def display(self):
		return f"Found SMB service was running on port ({self.port})"

	def get_port(self):
		return self.port

	def captured(self):
		return self.port



class Filtered_MSRPCServiceIsUp(AbstractFilteredObject):
	def __init__(self, port:str):
		self.port = port

	def display(self):
		return f"Found MSRPC service was running on port ({self.port})"

	def get_port(self):
		return self.port

	def captured(self):
		return self.port

