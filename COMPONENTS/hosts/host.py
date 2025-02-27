"""
This module describes the host object.
The host objects represents hosts in a Network. 

A host may have more than one role in the network. 
It can be several types of servers:
- SMB server 
- RPC server
- LDAP server
- NetBIOS workstation
This information is kept in the host. This way we can access
the servers and know what roles a host plays from other parts
of the code.
"""
import importlib
from pathlib import Path

from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

# components
from COMPONENTS.domains.domain import Domain
from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.ldap.ldapserver import LdapServer
from COMPONENTS.netbios.netbiosworkstation import NetBIOSWorkstation
from COMPONENTS.msrpc.msrpcserver import MSRPCServer
from COMPONENTS.smb.smbserver import SMBServer
from COMPONENTS.dns.dnsserver import DNSServer


# import the classes of techniques 
from .checkifmsrpcserviceisrunning import CheckIfMSRPCServiceIsRunning
from .checkifsmbserviceisrunning import CheckIfSMBServiceIsRunning
from .nbnsiptranslations import NBNSIPTranslation
from .portscan import PortScan
from .checkifdnsserviceisrunning import CheckIfDNSServiceIsRunning
from .checkifldapserviceisrunning import CheckIfLDAPServiceIsRunning

class Host(AbstractNetworkComponent):
	"""
	to add:
	- service scan 

	roles:
	- SMB server 
	- RPC server
	- LDAP server
	- NetBIOS workstation
		- NetBIOS SMB server (inside workstation)
		- NetBIOS DC (inside workstation)
	"""
	string_to_class = {
		"CheckIfMSRPCServiceIsRunning": CheckIfMSRPCServiceIsRunning, 
		"CheckIfSMBServiceIsRunning": CheckIfSMBServiceIsRunning,
		"CheckIfDNSServiceIsRunning": CheckIfDNSServiceIsRunning,
		"NBNSIPTranslation": NBNSIPTranslation, 
		"CheckIfLDAPServiceIsRunning":CheckIfLDAPServiceIsRunning,
		"PortScan": PortScan
	}
	methods = None
	
	def __init__(self, path:dict, ip:str=None,hostname:str=None):
		if hostname is not None:
			self.hostname = hostname     
		if ip is not None:
			self.ip = ip
		self.path = path.copy()
		self.path['host'] = self
		self.dc = False
		self.netbios_hostname = None
		self.netbios_groups = dict() # group_obj: roles
		self.dns_hostname = None
		self.fqdn = None
		self.domain = None # the domain object
		self.domain_role = None # the role this host has in the domain
		#self.ad_domain_roles = dict() # {domain_obj: role} - > the role might be None, 'DC' or 'PDC'
		self.roles = dict() # class_name: obj - > ex: 'NetBIOSWorkstation':nw_obj; 'LdapServer'
		self.ports = dict()
  
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)
		self.load_methods() 

	@classmethod
	def load_methods(cls):
		"""
		Loads the methods for this class. 
		The methods should be defined for this class name in config.json
		"""
		# lock this
		with sharedvariables.shared_lock:
			if cls.methods is None:  # Check if methods have already been loaded
				cls.methods = [] # initiate so it does not enter again
				
				# get the techniques for this class
				class_name = cls.__name__
				methods_config = sharedvariables.methods_config.get(class_name, {}).get("techniques", [])

				for class_entry in methods_config:
					class_name = class_entry["class"]
					if class_name in cls.string_to_class:
						_class = cls.string_to_class[class_name]
						cls.methods.append(_class)

	# getters

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"getting context for Host ({self.ip})")
			context = dict()
			context['ip'] = self.get_ip()
			context['network_address'] = self.get_network().get_network_address()
			context['interface_name'] = self.get_interface().get_interface_name()

			# for domain name 
			#(HOST IS DEPENDET OF DOMAIN)
			domain = self.get_domain()
			if domain is not None:
				context['domain_name'] = domain.get_domain_name()
			else:
				context['domain_name'] = None

			# hostname
			# (HOST IS DEPENDET OF NETBIOS WORKSTATION)
			context['netbios_hostname'] = self.get_netbios_hostname() # might be None
			return context


	def get_netbios_workstation_obj(self):
		with sharedvariables.shared_lock:
			logger.debug(f"getting netbios workstaion obj from Host ({self.ip})")

			if self.check_if_host_has_netbios_workstation_role():
				return self.roles['NetBIOSWorkstation']
			else:
				logger.debug(f"Host ({self.ip}) had no netbios workstation machine associated")
			return None


	def get_msrpc_server_obj(self):
		with sharedvariables.shared_lock:
			if self.check_if_host_has_rpc_server_role():
				return self.roles['MSRPCServer']
			return None


	def get_ldap_server_obj(self):
		"""
  		Retrieves the ldap server associated to this host
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Getting the ldap server for host ({self.get_ip()})")
			if 'LdapServer' not in self.roles:
				logger.debug(f"Host ({self.get_ip()}) didn't have a ldap server")
				return None
			return self.roles['LdapServer']


	def get_netbios_hostname(self):
		"""
		checks if the host has the netbios workstation role
		checks if the netbios workstation object has a hostname
		returns the hostname
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"getting netbios hostname for Host ({self.ip})")

			netbios_ws = self.get_netbios_workstation_obj()
			if netbios_ws is None:
				logger.debug(f"host ({self.ip}) doesn't have an associated netbios workstation")
				return None

			if netbios_ws.get_hostname() is None:
				logger.debug(f"host ({self.ip}) netbios workstation doesn't have a Hostname")
				return None

			hostname = netbios_ws.get_hostname()
			logger.debug(f"host ({self.ip}) netbios hostname is ({hostname})")
			return hostname
		return None

	def get_domain(self):
		with sharedvariables.shared_lock:
			if self.domain is None:
				return None
			return self.domain 
			if len(self.ad_domain_roles) != 0:
				domain_list = list(self.ad_domain_roles.keys())
				return domain_list[0] # only the first (and only) element
			return None

	def get_ip(self):
		with sharedvariables.shared_lock:
			return self.ip

	def get_root(self):
		with sharedvariables.shared_lock:
			return self.path['root']

	def get_interface(self):
		with sharedvariables.shared_lock:
			return self.path['interface']

	def get_network(self):
		with sharedvariables.shared_lock:
			return self.path['network']

	def get_host(self):
		with sharedvariables.shared_lock:
			return self.path['host']

	def get_dns_hostname(self):
		with sharedvariables.shared_lock:
			return self.dns_hostname

	

	"""
	Functions
	"""
				

	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['Host'] = dict()
			data['Host']['ip'] = self.get_ip()
			data['Host']['hostname'] = self.get_netbios_hostname()
			domain = self.get_domain()
			if domain is not None:
				domain_name = domain.get_domain_name()
			else:
				domain_name = None
			data['Host']['domain'] = domain_name
			data['Host']['roles'] = list()
			data['Host']['DNS hostname'] = self.get_dns_hostname() 
			# for each role i want to show what it has
			for role_name in self.roles:
				data['Host']['roles'].append(self.roles[role_name].display_json())
			return data


	def to_str(self):
		return f"{self.hostname}"

	def display(self):
		print(f"Host:{self.hostname}")

	def auto_function(self):
		for method in self.methods:
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		pass


	def merge_host_ip_with_another_host_hostname(self, host_hostname:'Host'):
		"""
		[IMPORTANT] : in the network don't forget to change the host in the
		hostname dict, otherwise it will just keep referencing the 'previous' host.

		The host_hostname is supposed to be the same host as this one. 
		We just found the hostname first when we didn't knew the ip address,
		and now we want to merge the information from the both.

		+ [IMPORTANT]: i will assume that it's impossible for us to have read 
		different services for the same port number. 

		only different values might be: ports, dc, hostname
		"""
		for port_number in host_hostname.ports:
			if port_number not in self.ports:
				self.ports[port_number] = host_hostname.ports[port_number]

		# if we knew that it was a DC, only using the hostname
		if host_hostname.dc != self.dc:
			if host_hostname.dc == True:
				self.dc = True

		# update the hostname
		self.hostname = host_hostname.hostname


	def activate_smb_methods(self):
		"""
		No smb methods for now.
		"""
		return []

	def add_role_to_netbios_group(self, role:str, group:str):
		if group not in self.netbios_groups:
			self.netbios_groups[group] = list()
		if role not in self.netbios_groups[group]:
			self.netbios_groups[group].append(role)
			if role == '1b':
				return [self.found_dc_methods] # the method to be run automatic
		
	def found_hostname_methods(self, hostname:str):
		"""
		the methods for when we found a hostname
		"""
		return [] # for now


	def check_if_host_has_domain(self):
		"""
  		Checks if host already has a domain
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"checking if host ({self.get_ip()}) already has domain")
			if self.domain is None:
				logger.debug(f"host ({self.get_ip()}) doesn't have a domain")
				return 
			return logger.debug(f"host ({self.get_ip()}) has domain ({self.domain.get_domain_name()})")
			if len(self.ad_domain_roles.keys()) > 0:
				logger.debug(f"host ({self.get_ip()}) is already part of a domain")
				return True
			return False


	def check_if_host_is_dc_for_domain(self, domain):
		"""
  		Checks if host is DC for a given domain
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"checking if host ({self.get_ip()}) already has domain")
			if self.domain is not None:
				if self.domain_role == 'DC' or self.domain_role == 'PDC':
					return True
			return False
			if domain in self.ad_domain_roles:
				role = self.ad_domain_roles[domain]
				if role is not None and role == 'DC':
					logger.debug(f"host ({self.get_ip()}) is DC of domain \
						({domain.get_domain_name()})")
					return True
			return False


	def check_for_ldap_server_role(self):
		"""
  		checks if this host has the ldap server role
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"checking if host ({self.get_ip()} has ldap server role)")
			if self.roles['LdapServer'] is None:
				logger.debug(f"host ({self.get_ip()}) does not have ldap server role")
				return False
			logger.debug(f"Host ({self.get_ip()}) has ldap server role")
			return True
 
	def add_role_ldap_server(self):
		"""
		adds a ldap server role to this host.
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Adding a ldap server role to this host ({self.get_ip()})")

			ldap_server = LdapServer(self)
			self.roles['LdapServer'] = ldap_server

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return ldap_server

	def get_or_add_role_ldap_server(self):
		"""
		If this host already has a role of ldap server returns the 
		ldap server object. Otherwise, creates and associates a new one
		"""
		with sharedvariables.shared_lock:
			ldap_server = self.get_ldap_server_obj()
			if ldap_server is None:
				ldap_server = self.add_role_ldap_server()
				
			return ldap_server



	# DNS
 
	def check_if_host_has_dns_server_role(self):
		with sharedvariables.shared_lock:
			logger.debug(f"Checking if host ({self.ip}) has a DNS server role")
			if 'DNSServer' not in self.roles:
				logger.debug(f"Host ({self.ip}) does not have a DNS server role")
				return False
			logger.debug(f"Host ({self.ip}) has a DNS server role")
			return True


	def get_dns_server_obj(self):
		"""
  		Retrieves the DNS server for this host or None
		"""
		with sharedvariables.shared_lock:
			if 'DNSServer' not in self.roles:
				return None
			return self.roles['DNSServer']

	def get_or_add_role_dns_server(self, port=str):
		"""
		Add and SMB server role to the host.
		First checks if it already has
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Host ({self.ip}) adding DNS server role")

			if self.check_if_host_has_dns_server_role():
				logger.debug(f"Host ({self.ip}) already had a DNS server role")
				return self.roles['DNSServer'] 
			else:
				dns_server_obj = DNSServer(self, port)
				self.roles['DNSServer'] = dns_server_obj

				# we updated this object
				sharedvariables.add_object_to_set_of_updated_objects(self)
	
				return dns_server_obj


	def found_dns_service_running_on_port(self, port=str):
		with sharedvariables.shared_lock:
			dns_server = self.get_or_add_role_dns_server(port)
			return dns_server
	
	def add_dns_hostname(self, dns_hostname):
		"""
  		Adds a dns hostname to this host.
		Checks if it already has one
	 	"""
		with sharedvariables.shared_lock:
			logger.debug(f"Adding dns hostname ({dns_hostname}) \
	   			for host ({self.ip})")
			if self.dns_hostname is not None:
				logger.debug(f"Host ({self.ip}) already had a \
					dns hostname")
			
			self.dns_hostname = dns_hostname
			return 


	# NETBIOS

	def add_role_netbios_workstation(self, netbios_hostname):
		"""
		Adds the role of netbios workstation. 
		If it already exists it does nothing.
		"""
		with sharedvariables.shared_lock:
			if 'NetBIOSWorkstation' not in self.roles:
				nbw_obj = NetBIOSWorkstation(host=self, hostname=netbios_hostname)
				self.roles['NetBIOSWorkstation'] = nbw_obj
				print("host is now considered also a netBIOS workstations")


	def associate_NetBIOSWorkstation(self, netbios_workstation:NetBIOSWorkstation):
		"""
		associates the netbios workstaiton to this host, 
		returns the automatic methods for the netbios workstation

		Updates the NetBIOSWorkstation object to point to this host
		as well
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Associating netbios workstation to Host ({self.ip})")
			self.roles['NetBIOSWorkstation'] = netbios_workstation

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return

	def check_if_host_has_netbios_workstation_role(self):
		with sharedvariables.shared_lock:
			logger.debug(f"checking if host ({self.ip}) has a netbios workstation role")
			if 'NetBIOSWorkstation' not in self.roles:
				logger.debug(f"Host ({self.ip}) does not have a netbios workstation role")
				return False
			logger.debug(f"Host ({self.ip}) has a netbios workstation role")
			return True

	def add_role_netbios_workstation(self, hostname=None):
		"""
		Adds the role of netbios workstation to the host.
		It also creates the object, hostname might be empty. 
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Host ({self.ip}) adding netbios workstation role")
			if self.check_if_host_has_netbios_workstation_role():
				logger.debug(f"Host ({self.ip}) already had netbios workstation role")
			else:
				netbios_workstation_obj = NetBIOSWorkstation(self, hostname)
				self.roles['NetBIOSWorkstation'] = netbios_workstation_obj


	def associate_existing_netbios_group_to_host_ip(self, netbios_group):
		"""
		gets or creates the netbios workstation role 
		associates an existing netbios group to it.
		"""

		# with lock update the information on the netbios group
		with sharedvariables.shared_lock:
			netbios_ws = self.get_netbios_workstation_obj()
			if netbios_ws is None:
				self.add_role_netbios_workstation(hostname=None)
				netbios_ws = self.get_netbios_workstation_obj()
			netbios_ws.add_group(netbios_group) # empty list of list with auto functions

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
		return



	# SMB

	def check_if_host_has_smb_server_role(self):
		with sharedvariables.shared_lock:
			logger.debug(f"Checking if host ({self.ip}) has a smb server role")
			if 'SMBServer' not in self.roles:
				logger.debug(f"Host ({self.ip}) does not have a smb server role")
				return False
			logger.debug(f"Host ({self.ip}) has a smb server role")
			return True


	def get_smb_server_obj(self):
		"""
  		Retrieves the smb server for this host or None
		"""
		with sharedvariables.shared_lock:
			if 'SMBServer' not in self.roles:
				return None
			return self.roles['SMBServer']

	def get_or_add_role_smb_server(self, port=str):
		"""
		Add and SMB server role to the host.
		First checks if it already has
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Host ({self.ip}) adding smb server role")

			if self.check_if_host_has_smb_server_role():
				logger.debug(f"Host ({self.ip}) already had a smb server role")
				return self.roles['SMBServer'] 
			else:
				smb_server_obj = SMBServer(self, port)
				self.roles['SMBServer'] = smb_server_obj

				# we updated this object
				sharedvariables.add_object_to_set_of_updated_objects(self)
	
				return smb_server_obj


	def found_smb_service_running_on_port(self, port=str):
		with sharedvariables.shared_lock:
			smb_server = self.get_or_add_role_smb_server(port)
			return smb_server



	# RPC


	def check_if_host_has_rpc_server_role(self):
		with sharedvariables.shared_lock:
			logger.debug(f"Checking if host ({self.ip}) has rpc server role")
			if 'MSRPCServer' not in self.roles:
				logger.debug(f"Host ({self.ip}) does not have a rpc server role")
				return False
			logger.debug(f"Host ({self.ip}) has a rpc server role")
			return True

	def get_or_add_role_rpc_server(self, port=str):
		"""
		get's the existing rpc server role or adds a new one
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Host ({self.ip}) adding rpc server role")

			if self.check_if_host_has_rpc_server_role():
				logger.debug(f"host ({self.ip}) already has a rpc server role")
				return self.roles['MSRPCServer']
			else:
				msrpc_server = MSRPCServer(self, port)
				self.roles['MSRPCServer'] = msrpc_server
				logger.debug(f"Added MSRPC server role to ({self.ip})")

				# we updated this object
				sharedvariables.add_object_to_set_of_updated_objects(self)
				return msrpc_server


	def found_msrpc_service_running_on_port(self, port):
		with sharedvariables.shared_lock:
			msrpc_server = self.get_or_add_role_rpc_server(port)
			return msrpc_server




	# LDAP 
	def check_if_host_has_ldap_server_role(self):
		with sharedvariables.shared_lock:
			logger.debug(f"Checking if host ({self.ip}) has a LDAP server role")
			if 'LdapServer' not in self.roles:
				logger.debug(f"Host ({self.ip}) does not have a LDAP server role")
				return False
			logger.debug(f"Host ({self.ip}) has a LDAP server role")
			return True


	def get_ldap_server_obj(self):
		"""
  		Retrieves the DNS server for this host or None
		"""
		with sharedvariables.shared_lock:
			if 'LdapServer' not in self.roles:
				return None
			return self.roles['LdapServer']

	def get_or_add_role_ldap_server(self, port=str):
		"""
		Add and SMB server role to the host.
		First checks if it already has
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Host ({self.ip}) adding LDAP server role")

			if self.check_if_host_has_ldap_server_role():
				logger.debug(f"Host ({self.ip}) already had a LDAP server role")
				return self.roles['LdapServer'] 
			else:
				ldap_server_obj = LdapServer(self)
				self.roles['LdapServer'] = ldap_server_obj

				# we updated this object
				sharedvariables.add_object_to_set_of_updated_objects(self)
	
				return ldap_server_obj


	def found_ldap_service_running_on_port(self, port=str):
		with sharedvariables.shared_lock:
			ldap_server = self.get_or_add_role_ldap_server(port)
			return ldap_server





	# Domains
 
	def add_dc_services(self):
		"""
  		When we find that a host is a domain controller.
		Since certain services are mandatory for domain controllers to have 
	 	we don't have to enumerate the host to know that they're there.
	  	SMB, MSRPC, LDAP.
	   	"""
		# If we don't have the MSRPC role
		if not self.check_if_host_has_rpc_server_role():
			self.get_or_add_role_rpc_server('135')
		if not self.check_if_host_has_smb_server_role():
			self.get_or_add_role_smb_server('445')
		if not self.check_for_ldap_server_role():
			self.get_or_add_role_ldap_server()
		return 



	def associate_host_services_to_domain(self, domain:Domain):
		"""
  		Associates the host services to a domain.
		"""
		with sharedvariables.shared_lock:
			# for each service -> associate this domain
			for role_key in self.roles:
				role_obj = self.roles[role_key]
				role_obj.associate_domain(domain) # might do nothing
			return 


	def add_domain(self, domain:Domain):
		"""
  		Adds the domain to this host. 
		The host will know to which domain it belongs
  		"""
		with sharedvariables.shared_lock:
			logger.debug(f"associating domain ({domain.get_domain_name()})\
	   			to host ({self.get_ip()})")

			associated_domain = self.get_domain()
			if associated_domain is not None:
				logger.debug(f"Host ({self.get_ip()}) is already associated \
					to a domain ({associated_domain.get_domain_name()})")
				return 

			self.domain = domain
			self.domain_role = None # still no particular role
			#self.ad_domain_roles[domain] = None # only machine level for now
			logger.debug(f"associated domain ({domain.get_domain_name()}) \
	   			to host ({self.get_ip()}) successfully")

			# the object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 
	

	def associate_domain_to_host_if_not_already(self, domain:Domain):
		"""
		+ Checks if it has a domain associated
		+ (if not) adds this new domain to the dictionary
		+ gives the role of None (machine) to the roles

		calls methods if it was updated
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"associating domain ({domain.get_domain_name()})\
	   			to host ({self.get_ip()})")

			associated_domain = self.get_domain()
			if associated_domain is not None:
				logger.debug(f"Host ({self.get_ip()}) is already associated \
					to a domain ({associated_domain.get_domain_name()})")
				return 

			self.domain = domain
			self.domain_role = None # still no role for now
			#self.ad_domain_roles[domain] = None # only machine level for now
			logger.debug(f"associated domain ({domain.get_domain_name()}) \
	   			to host ({self.get_ip()}) successfully")
   
			self.associate_host_services_to_domain(domain)
	
			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 


	def associate_DC_role_to_associated_domain(self, domain:Domain):
		with sharedvariables.shared_lock:
			logger.debug(f"associating role DC to host's ({self.get_ip()}) associated domain")
			domain = self.get_domain()

			# if not associated to any domain
			if domain is None:
				logger.debug(f"Host ({self.get_ip()}) was not associated to a domain")
				return 
			# if it's already a PDC or DC
			if self.domain_role == 'DC' or self.domain_role == 'PDC':
				return 
			#if self.ad_domain_roles[domain] is not None and self.ad_domain_roles[domain] == 'PDC':
			#	return 

			self.ad_domain_roles[domain] = 'DC' # hard coded


	def associate_PDC_role_to_associated_domain(self, domain:Domain):
		with sharedvariables.shared_lock:
			logger.debug(f"associating role PDC to host's ({self.get_ip()}) associated domain")
			domain = self.get_domain()
			if domain is None:
				logger.debug(f"Host ({self.get_ip()}) was not associated to a domain")

			self.domain_role = 'PDC'
			#self.ad_domain_roles[domain] = 'PDC' # hard coded


	def found_domain_for_host_methods(self):
		"""
		the list of functions to call when we know we found a domain for this host.
		Call Mandatory Methods (host.found_domain_methods) 
		+ check for SMB service 
		+ check for RPC service
		+ check for LDAP service
		+ check for DNS service
		+ check for Kerberos service

		For each role checks if there are functions to be called.
		"""
		with sharedvariables.shared_lock:
			auto_functions = list()
			auto_functions += [self.found_domain_methods]
	
			# call the specific methods for each
			for role_name in self.roles:
				role_obj = self.roles[role_name]
				auto_functions += role_obj.found_domain_methods()
			return auto_functions




