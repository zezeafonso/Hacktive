import queue
import threading 
import multiprocessing

import SpecificExceptions as SE
import Methods
from AbstractClasses import AbstractNetworkComponent
import ThreadShares as TS
from Events import Run_Event


def throw_run_event_to_command_listener(event:Run_Event) -> None:
	TS.cmd_queue.put(event)



class Port(AbstractNetworkComponent):
	def __init__(self, port_number:str, service:str):
		self.port_number = port_number
		self.service = service

	def display(self):
		pass

	def updateComponent(self, add_nc:AbstractNetworkComponent):
		pass

	def auto(self):
		if self.service == 'domain':
			return []
		elif self.service == 'kerberos-sec':
			return []
		elif self.service == 'microsoft-ds' or port_number == '445' or port_number == '135':
			return []
		elif self.service == 'ldap':
			return []
		elif self.service == 'msrpc':
			return []
		else:
			return []



class NetBIOSGroupDC:
	def __init__(self, host:'Host', group:'NetBIOSGroup'):
		self.host = host
		self.group = group

	def auto(self):
		"""
		for now doesn't do anything.
		what we want it to do:
		+ call the ldapsearch for this machines
		+ find the other machines that have this group
		"""
		print("CALLED AUTO FOR DC")
		pass

class NetBIOSGroupPDC:
	def __init__(self, host:'Host', group:'NetBIOSGroup'):
		self.host = host
		self.group = group

	def auto(self):
		"""
		for now doesn't do nothing.
		What we want it to do:
		+ call the ldapsearch for the naming contexts
		"""
		print("CALLED AUTO FOR PDC")
		pass # for now

class NetBIOSMBServer:
	def __init__(self, host:'Host'):
		self.host = host

		# call automatic methods listed for this object
		# or put them in a list to be send
	

	def auto(self):
		"""
		Nothing for now.
		what we would like:
		+ to check if the smb is active -> if it is create the actual smb server 
		+ to check for the shares in that smb  
		"""
		print("CALLED AUTO FOR NETBIOS SERVER")
		pass



class NetBIOSWorkstation:
	def __init__(self, host:'Host', hostname:str=None):
		self.host = host
		self.hostname = hostname
		self.groups_and_roles = dict() # group_name : [role1, role2]
		self.smb_server = None

		# call automatic methods listed for this one bro

	def update_hostname(self, hostname:str):
		"""
		It can happen that we create the netbios workstation 
		without a hostname, depending on the filtered objects
		we receive first.
		This function updates the hostname value .
		"""
		with TS.shared_lock:
			if self.hostname is not None:
				if self.hostname != hostname:
					print("conflicting hostnames for the same machine !!")
			self.hostname = hostname

	def associate_new_group_without_roles(self, group:'NetBIOSGroup'):
		"""
		Associates a new group to this netbios workstation
		without roles means that we have no particular feature 
		for this workstation listed in the netbios so far.
		"""
		with TS.shared_lock:
			self.groups_and_roles[group] = []

	def check_if_belongs_to_group(self, group:'NetBIOSGroup'):
		"""
		checks if a groups is present inside the groups and
		roles dictionary
		"""
		with TS.shared_lock:
			return group in self.groups_and_roles

	def get_roles_associated_to_group(self, group:'NetBIOSGroup'):
		"""
		Retrives the roles associated with a group.
		The group might not be present in groups and roles
		as such we return None in that case
		"""
		with TS.shared_lock:
			if self.check_if_belongs_to_group(group):
				return self.groups_and_roles[group]
			else:
				return None

	def check_if_role_already_exists_for_group(self, group:'NetBIOSGroup', role_class):
		"""
		Checks for the presence of duplicate objects of the same 
		class for a group. This behaviour should not happen and 
		this check prevents we inserting duplicates
		"""
		with TS.shared_lock:
			roles = self.get_roles_associated_to_group(group)
			if roles == None: # the group is not present 
				return False
			for role in roles:
				if isinstance(role, role_class):
					return True
			return False
	
	def add_new_role_to_group(self, group:'NetBIOSGroup', role):
		"""
		The function that adds a role to a group in 
		groups and roles.
		Does not perform the checks of:
		the groups is present or not 
		the role is already in or not
		"""
		with TS.shared_lock:
			self.groups_and_roles[group].append(role)

	def create_and_associate_netbios_dc_group_role(self, group:'NetBIOSGroup'):
		"""
		creates the NetBIOSGroupDC and associates it to a group
		that MUST already be associated.

		checks if the NetBIOSGroupDC is already present in that 
		group.
		"""
		with TS.shared_lock:
			netbios_dc = NetBIOSGroupDC(self.host, group)
			if not self.check_if_role_already_exists_for_group(group, NetBIOSGroupDC):
				self.add_new_role_to_group(group, netbios_dc)
				return [netbios_dc.auto]
			return []



	# PUBLIC methods
	def get_groups(self):
		with TS.shared_lock:
			return [group for group in self.groups_and_roles]

	def add_netbios_smb_server(self, group:'NetBIOSGroup'):
		# check if the group is already in the class
		# if it isn't
			# create the netbiosGroupsSMBServer
			# insert the object to this group in dict
		pass

	def add_pdc_role_for_group(self, group:'NetBIOSGroup'):
		"""
		Adds a pdc role for an existing group. 

		Checks if the role is already in that group.
		If not -> add it.
		returns methods 
		"""
		with TS.shared_lock:
			if not self.check_if_role_already_exists_for_group(group, NetBIOSGroupPDC):
				role = NetBIOSGroupPDC(self.host, group)
				self.add_new_role_to_group(group, role)
				return [role.auto]
			return []


	def add_group(self, group:'NetBIOSGroup'):
		"""
		Adds a group to which this netBIOS Workstation belongs
		If the group is already associated does nothing

		There is a difference between 00 groups and 1c groups 
		1c indicates that this host is listed as a Domain Controller
		for the domain/group.

		If so we first check if there is already a dc group member role
		if not: create the role of DC group member to that group
		and associate it in the dict groups and roles

		returns methods
		"""
		with TS.shared_lock:
			if self.check_if_belongs_to_group(group):
				return []
			else:
				print(group)
				print(group.type)

				# place the group in dict without roles
				self.associate_new_group_without_roles(group)

				# domain controller role
				if group.type == '1c':
					return self.create_and_associate_netbios_dc_group_role(group)

				# if no new feature was added
				return []



	def get_group_from_group_id(self, group_id:str):
		"""
		Returns the groups object that this netbios workstation belongs 
		to that possesses that group_id.
		"""
		with TS.shared_lock:
			groups = self.get_groups()
			for group in groups:
				if group.id == group_id:
					return group
			return None


	def get_netbios_group_dc_from_group(self, group:'NetBIOSGroup'):
		"""
		attains the netbios group dc from a group that is associated.
		"""
		with TS.shared_lock:
			if self.check_if_belongs_to_group(group):
				roles = self.get_roles_associated_to_group(group)
				for role in roles:
					if isinstance(role, NetBIOSGroupDC):
						return role
			return []

	def add_netbios_smb_server(self):
		"""
		Add the role of netbios Smb server to this netbios workstation
		Check if it's already there
		"""
		with TS.shared_lock:
			if self.smb_server is not None:
				return []
			netbios_smb_server = NetBIOSMBServer(self.host)
			self.smb_server = netbios_smb_server
			return [netbios_smb_server.auto]


class Host(AbstractNetworkComponent):
	"""
	to add:
	- service scan 
	- hostname translation
	"""
	#methods = {Methods.PortScan._name: Methods.PortScan}
	methods = {Methods.NBNSIPTranslation._name: Methods.NBNSIPTranslation}
	ports = dict()
	hostname = None
	ip = None
	dc = False
	netbios_hostname = None
	netbios_groups = dict() # each group will hold a list of the roles this machines takes
	DNS_hostname = None
	fqdn = None
	roles = dict()
	
	def __init__(self, path:dict, ip:str=None,hostname:str=None):
		if hostname is not None:
			self.hostname = hostname     
		if ip is not None:
			self.ip = ip
		self.path = path.copy()
		self.path['host'] = self

	def to_str(self):
		return f"{self.hostname}"

	def display(self):
		print(f"Host:{self.hostname}")

	def auto(self):
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self)
			for event in list_events:
				throw_run_event_to_command_listener(event)
		pass

	def update_hostname(self, hostname:str):
		if self.hostname is not None:
			if self.hostname != hostname:
				print("Found new hostname: {hostname} for host with ip: {self.ip} and hostname {self.hostname}")
		else:
			self.hostname = hostname
			# TODO - CALL AUTO METHODS FOR THIS (NOTHING FOR NOW)

	def get_ip(self):
		return self.ip

	def updateComponent(self, add_nc:AbstractNetworkComponent):
		if isinstance(add_nc, Port):
			if add_nc.port_number in self.ports:
				pass
			else:
				self.ports[add_nc.port_number] = add_nc
				if not self.dc:
					dc_services = ['domain', 'kerberos-sec', 'msrpc', 'ldap', 'microsoft-ds']
					# Check if all elements are in the dictionary
					all_present = all(service in services_dict for service in dc_services)
					if all_present:
						self.dc = True
						print(f"[+] We found a new DC with ip: {self.ip}")

		else:
			raise SE.NoUpdateComponentForThatClass()


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


	def activate_port(self, port_number:str):
		# the port was already found
		if port_number in self.ports:
			return [] # no new methods
		else:
			self.ports[port_number] = Port(port_number=port_number, service='')
			auto_methods = self.ports[port_number].auto()
			return auto_methods

	def activate_smb_methods(self):
		"""
		No smb methods for now.
		"""
		return []

	def update_netbios_group(self, group_name:str):
		if group_name in self.netbios_groups:
			pass
		elif group_name not in self.netbios_groups:
			self.netbios_groups[group_name] = list() # emtpy list

	def add_role_to_netbios_group(self, role:str, group:str):
		if group not in self.netbios_groups:
			self.netbios_groups[group] = list()
		if role not in self.netbios_groups[group]:
			self.netbios_groups[group].append(role)
			if role == '1b':
				return [self.found_dc_methods] # the method to be run automatic


	def found_dc_methods(self):
		"""
		the methods for when we find a dc
		"""
		dc_methods = [Methods.QueryNamingContextOfDCThroughLDAP]
		for method in dc_methods:
			list_events = method.create_run_events(self)
			for event in list_events:
				throw_run_event_to_command_listener(event)
		

	def found_hostname_methods(self, hostname:str):
		"""
		the methods for when we found a hostname
		"""
		return [] # for now

	def check_if_ldap_domain_components_path_is_domain_path(self, domain_components_path):
		"""
		Checks if the domain components path found in ldap
		ex: foxriver.local... domaindnszones.foxriver.local 
		is in fact a domain path. 
		For this we check if we belong to any group of netbios 
		that starts with the same word. 
		in our case the host will belong to foxriver and so 
		'foxriver.local' is in fact a domain name 
		"""
		first_word_of_dcs = domain_components_path.split('.')[0]
		with TS.shared_lock:
			for group in self.netbios_groups:
				if first_word_of_dcs.lower() == group.lower():
					print(f"FOUND IT: DOMAIN NAME: {domain_components_path}")
					return []
			return []


	def add_role_netbios_workstation(self, netbios_hostname):
		"""
		Adds the role of netbios workstation. 
		If it already exists it does nothing.
		"""
		with TS.shared_lock:
			if 'NetBIOSWorkstation' not in self.roles:
				nbw_obj = NetBIOSWorkstation(host=self, hostname=netbios_hostname)
				self.roles['NetBIOSWorkstation'] = nbw_obj
				print("host is now considered also a netBIOS workstations")


	def add_role_netbios_workstation(self, hostname=None):
		"""
		Adds the role of netbios workstation to the host.
		It also creates the object, hostname might be empty. 
		"""
		with TS.shared_lock:
			if 'NetBIOSWorkstation' not in self.roles:
				netbios_workstation_obj = NetBIOSWorkstation(self, hostname)
				self.roles['NetBIOSWorkstation'] = netbios_workstation_obj


	# getters and setters

	def get_netbios_workstation_obj(self):
		with TS.shared_lock:
			if 'NetBIOSWorkstation' in self.roles:
				return self.roles['NetBIOSWorkstation']
			return None

	def get_root(self):
		return self.path['root']

	def get_interface(self):
		return self.path['interface']

	def get_network(self):
		return self.path['network']

	def get_host(self):
		return self.path['host']




class NetBIOSGroup():

	def __init__(self, group_name, group_type):
		"""
		The type of the group clarifies if this is <00> or <1c>
		"""
		self.name = group_name
		self.type = group_type
		self.id = group_name.lower()+'#'+group_type
		self.associated = None # the object to which is associated (network / wins server)

	def add_group_member(self):
		"""
		Function to add a group member to a netBIOS group
		this way we can also get the member through here
		"""
		pass

	def auto_methods(self):
		"""
		Defines the functions that runs the automatic methods 
		for when we find a new netBIOS group.

		You should only do this, whenever you associate the group object 
		to another object, the methods here are for when you find a new
		netbios group. In our case the object must be associated with 
		the network or wins server so that the methods work.
		"""
		# I want for us to find the other bitches that belong to this one
		# TODO : add the method for nmblookup that finds the other ip's for this group
		methods = [Methods.NBNSGroupMembers]
		list_events = []
		for method in methods:
			list_events += method.create_run_events(self)
		for event in list_events:
			throw_run_event_to_command_listener(event)

	def associate_with_object(self, obj):
		"""
		Associates this network group, with something, most likely 
		the network or subnet where we are present.
		"""
		if isinstance(obj, Network):
			with TS.shared_lock:
				if self.associated is not None:
					print("changing the associated object of netbios group")
				self.associated = obj




class Network(AbstractNetworkComponent):
	"""
	to add:
	- get the dns server for it

	"""
	methods = {Methods.ArpScan._name: Methods.ArpScan}
	#methods = {}
	network_address = None
	hosts = None
	path = None
	netbios_groups = dict()
	
	def __init__(self, network_address:str, path:dict):
		self.network_address = network_address
		#TODO: search for hosts using ip address
		self.hosts = {}
		self.hostnames = {} # point to the same hosts as hosts, but uses hostnames
		self.path = path.copy()
		self.path['network'] = self

	def auto(self):
		print("auto network")
		# no need for lock, the methods don't change
		list_events = []
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self)
			for event in list_events:
				throw_run_event_to_command_listener(event)

	def add_our_ip(self, ip:str):
		self.our_ip = ip

	# LOCK
	def attach_host(self, ip:str):
		with TS.shared_lock:
			if ip in self.hosts:
				pass
			else:
				# TODO: must also accept hostnames
				print(f"creating new host: {ip}")
				new_host = Host(ip=ip, path=self.path)
				self.hosts[ip] = new_host
				return new_host

	# PLEASE USE A LOCK
	def check_for_host_with_ip(self, host_ip:str):
		"""
		if host exists, return the object
		"""
		if host_ip in self.hosts:
			return {'exists':'yes', 'object':self.hosts[host_ip]}
		return {'exists':'no'}

	# PLEASE USE A LOCK
	def create_host_with_ip(self, ip:str):
		"""
		creates the host; attaches it to the network obj;
		returns the list of methods to run
		"""
		new_host_obj = Host(ip=ip, path=self.path)
		self.hosts[ip] = new_host_obj
		res = {'object': new_host_obj, 'methods':self.found_ip_host_methods(new_host_obj)}
		return res

	# PLEASE USE A LOCK
	def found_ip_host_methods(self, host:Host):
		"""
		the methods that we'll run when we find a host
		MUST RETURN A LIST
		"""
		return [host.auto]

	def reference_new_host_using_NetBIOS_hostname(self, host:Host, hostname:str):
		self.hostnames[hostname] = host
	
	def attach_NetBIOS_hostname_to_ip_host(self, hostname:str, ip:str) -> list:
		# TODO: check if the hostname didn't already exist in the self.hostnames
		# get the host with the ip
		ip_host = self.hosts[ip]
		
		# check if the host with that hostname exists, 
		if ip_host.hostname != None:
			# we found a different one
			if ip_host.hostname != hostname:
				print(f"We found a new hostname {hostname} for a host {ip} that already had a hostname {self.hostname}")
				return []
			# we found the same one
			if ip_host.hostname == hostname:
				return []

		# check if the hostname was referencing a host
		if hostname in self.hostnames:
			# merge information with the ip host (will give methods)
			ip_host.merge_host_ip_with_another_host_hostname(self.hostnames[hostname])
			# update the hostname referencing
			self.reference_new_host_using_NetBIOS_hostname(host=ip_host, hostname=hostname)
			return []

		# if it's a completely new hostname
		else: 
			# update the hostname in host
			ip_host.update_hostname(hostname)
			# reference a host using hostname
			self.reference_new_host_using_NetBIOS_hostname(host=ip_host, hostname=hostname)
			return ip_host.found_hostname_methods(hostname)


	"""
	returns:
	+ host object
	+ auto methods to call (only if we found something new)
	"""
	def found_NetBIOS_hostname(self, hostname:str):
		if hostname in self.hostnames:
			return {'object':self.hostnames[hostname], 'methods':[]}
		else:
			# create hostname
			host_hostname = Host(hostname=hostname, path=self.path)
			# reference it
			self.reference_new_host_using_hostname(host=host_hostname, hostname=hostname)
			methods_to_call = host_hostname.found_hostname_methods(hostname)
			return {'object':host_hostname, 'methods':methods_to_call}

	def get_host_with_ip(self, ip:str):
		if ip not in self.hosts:
			return None
		return self.hosts[ip]

	def updateComponent(self, add_nc:AbstractNetworkComponent):
		if isinstance(add_nc, Host):
			print(f"[+] Found new Livehost {add_nc.ip} for network {self.network_address}")
			self.hosts[add_nc.ip] = add_nc
		pass


	def check_if_netbios_group_exists(self, group_name:str, _type:str):
		with TS.shared_lock:
			res = False
			group_id = group_name.lower() + '#'+_type
			if group_id in self.netbios_groups:
				res =  True
		return res    

	def create_netbios_group(self, group_name:str, group_type:str):
		"""
		Creates a new netbios group for this network.
		Returns the object and the automatic methods to run 
		(we found a new netbios group)
		"""
		answer = dict()
		answer['object'] = NetBIOSGroup(group_name, group_type)
		answer['methods'] = [] # don't call any methods here. 
		return answer

	def associate_netbios_group_to_this_network(self, group:NetBIOSGroup):
		with TS.shared_lock:
			if not self.check_if_netbios_group_exists(group.name, group.type):
				group_id = group.name+'#'+group.type
				self.netbios_groups[group_id] = group


	"""
	getters and setters
	"""    

	def get_network_address(self):
		n_a = None
		with TS.shared_lock:
			n_a = self.network_address
		return n_a

	def get_root(self):
		return self.path['root']

	def get_interface(self):
		return self.path['interface']

	def get_network(self):
		return self.path['network']

	def to_str(self):
		return f"{self.network_address}"



class Interface(AbstractNetworkComponent):
	"""
	add: 
	- dhcp broadcast discover 
	- responder analyzer (more on this later)
	"""
	methods = {}
	path = {}

	def __init__(self, interface_name:str, path:dict):
		self.interface_name = interface_name
		self.networks = {}
		self.path = path.copy()
		self.path['interface'] = self

	def add_network(self, network:Network):
		# TODO: check if already exists
		self.networks[network.network_address] = network

	# LOCK
	def attach_network(self, network_name:str):
		with TS.shared_lock:
			if network_name in self.networks:
				pass
			else:
				print(f"creating new network: {network_name}")
				new_network = Network(network_name, self.path)
				self.networks[network_name] = new_network
				return new_network

	# please use a LOCK
	def check_for_network_str(self, network_name:str):
		"""
		if network exists, return the object
		"""
		if network_name in self.networks:
			return {'exists': 'yes', 'object': self.networks[network_name]}
		return {'exists':'no'}

	def create_network_with_network_str(self, network_name:str):
		"""
		creates the network; attaches it to the interface obj;
		returns the list of methods to run
		"""
		new_network_obj = Network(network_name, self.path)
		self.networks[network_name] = new_network_obj
		res = {'object': new_network_obj, 'methods':self.found_network_methods(new_network_obj)}
		return res

	def found_network_methods(self, network:Network):
		"""
		the methods that we'll run when we find a network
		MUST RETURN A LIST
		"""
		return [network.auto]

	def get_network(self, network_name:str):
		if network_name not in self.networks:
			return None
		return self.networks[network_name]

	def user_interaction(self, banner:str):
		self.display()
		interface_banner = banner+' '+self_interface_name+' >'
		while True:
			user_choice = input(interface_banner)

			if user_choice == 'display':
				self.display()
			elif user_choice in self.networks:
				network = self.networks[user_choice]
				network.user_interaction(interface_banner)
			else:
				print("typo, try again")
				continue

	"""
	Run this when we find a new interface
	"""
	def auto(self):
		print("auto for interface")
		return # NOTHING FOR NOW
		# no need for lock, the methods don't change
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self)
			for event in list_events:
				throw_run_event_to_command_listener(event)

	def display(self):
		print(f"Interface: {self.interface_name}")
		display_str = "networks:\n"
		for network_address in self.networks:
			display_str += " - "+self.networks[network_address].to_str() + '\n'
			display_str += "methods:"
		for method in self.__class__.methods:
			continue
		print(display_str)

	def updateComponent(self, nc_to_add:AbstractNetworkComponent):
		if isinstance(nt_to_add, Network):
			print(f"[+] Found new network {nc_to_add.network_address} for interface {self.interface_name}")
			self.add_network(nc_to_add)
		else:
			raise SE.NoUpdateComponentForThatClass()

	def get_root(self):
		return self.path['root']

	def get_interface(self):
		return self.path['interface']

	def get_interface_name(self):
		return self.interface_name




class Root(AbstractNetworkComponent):
	methods = {Methods.ListInterfaces._name: Methods.ListInterfaces}

	def __init__(self):
		self.interfaces = {}
		self.path = {'root':self} # the path to this object

	def add_interface(self, interface:Interface):
		# call the methods from the interface
		self.interfaces[interface.interface_name] = interface

	# LOCK.
	# if new object return it 
	def attach_interface(self, interface_name:str):
		with TS.shared_lock:
			if interface_name in self.interfaces:
				pass
			else:
				print(f"creating new interface: {interface_name}")
				new_interface = Interface(interface_name, self.path)
				self.interfaces[interface_name] = new_interface
				return new_interface

	def get_interface(self, interface_name:str):
		if interface_name not in self.interfaces:
			return None
		return self.interfaces[interface_name]

	# please use a LOCK
	def check_for_interface_name(self, interface_name:str):
		"""
		if interface exists, return the object
		"""
		if interface_name in self.interfaces:
			return {'exists': 'yes', 'object': self.interfaces[interface_name]}
		return {'exists':'no'}

	def create_interface_with_name(self, interface_name:str):
		"""
		creates the interface; attaches it to the root obj;
		returns the list of methods to run
		"""
		new_interface_obj = Interface(interface_name, self.path)
		self.interfaces[interface_name] = new_interface_obj
		res =  {'object':new_interface_obj, 'methods':self.found_interface_methods(new_interface_obj)}
		return res

	def found_interface_methods(self, interface:Interface):
		"""
		the methods that we'll run when we find a interface
		MUST BE A LIST
		"""
		return [interface.auto]
		

	# TODO: do with lock
	def updateComponent(self, nc_to_add:AbstractNetworkComponent):
		if isinstance(nc_to_add, Interface):
			print(f"Found new interface: {nc_to_add.interface_name} with networks: {nc_to_add.networks}")
			self.add_interface(nc_to_add)
		else:
			raise SE.NoUpdateComponentForThatClass()

	def auto(self, banner:str = 'console >'):
		# no need for lock, the methods don't change
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self)
			for event in list_events:
				throw_run_event_to_command_listener(event)


	def get_root(self):
		return self.path['root']
