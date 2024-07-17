from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.hosts.host import Host
from COMPONENTS.netbios.netbiosgroup import NetBIOSGroup
from COMPONENTS.netbios.netbiosworkstation import NetBIOSWorkstation

from COMPONENTS.network.arpscan.method import ArpScan


class Network(AbstractNetworkComponent):
	"""
	to add:
	- get the dns server for it

	"""
	methods = {ArpScan}
	
	def __init__(self, network_address:str, path:dict):
		self.network_address = network_address
		#TODO: search for hosts using ip address
		self.hosts = {}
		self.hostnames = {} # point to the same hosts as hosts, but uses hostnames
		self.netbios_workstations = []
		self.path = path.copy()
		self.path['network'] = self
		self.netbios_groups = dict() # group id : group object
		self.netbios_workstations = [] # [netbiosworkstation_obj, netbiosworkstaiton_obj]
		self.our_ip = None # for now we don't have an IP in the network

		# the current context of the object
		self.state = None
		# the objects that depend on the context from the network
		self.dependent_objects = list()

		# too call the automatic methods
		self.check_for_updates_in_state()

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"getting context for network ({self.network_address})")
			context = dict()
			context['network_address'] = self.get_network_address()
			context['interface_name'] = self.get_interface().get_interface_name()
			context['our_ip'] = self.get_our_ip()
			return context

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with sharedvariables.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def get_network_address(self):
		n_a = None
		with sharedvariables.shared_lock:
			n_a = self.network_address
		return n_a

	def get_our_ip(self):
		return self.our_ip

	def get_host_through_ip(self, ip):
		with sharedvariables.shared_lock:
			logger.debug(f"getting host associated to the network ({self.network_address}) through ip ({ip})")
			if ip not in self.hosts:
				logger.debug(f"This network ({self.network_address}) is not associated with a host with ip: ({ip})")
				return None
			return self.hosts[ip]

	def get_root(self):
		return self.path['root']

	def get_interface(self):
		return self.path['interface']

	def get_network(self):
		return self.path['network']

	def to_str(self):
		return f"{self.network_address}"


	# Functions

	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['network'] = dict()
			data['network']['address'] = self.network_address
			data['network']['netbios groups'] = list()
			for netbios_group_id in self.netbios_groups:
				# change I want to see who's in the group
				data['network']['netbios groups'].append(self.netbios_groups[netbios_group_id].id)
			data['network']['Hosts'] = list()
			for host_ip in self.hosts:
				# i want to see what's in the ip 
				data['network']['Hosts'].append(self.hosts[host_ip].display_json())
			data['network']['netbios workstations'] = list()
			for netbios_workstation in self.netbios_workstations:
				# i want to see each of the roles
				data['network']['netbios workstations'].append(netbios_workstation.display_json())
			return data

	def auto_function(self):
		# no need for lock, the methods don't change
		list_events = []
		for method in self.methods:
			list_events = method.create_run_events(self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def add_our_ip(self, ip:str):
		with sharedvariables.shared_lock:
			self.our_ip = ip

			# because we update the object -> check for relevance
			self.check_for_updates_in_state()
			return 

	def attach_host(self, ip:str):
		with sharedvariables.shared_lock:
			if ip in self.hosts:
				pass
			else:
				# TODO: must also accept hostnames
				print(f"creating new host: {ip}")
				new_host = Host(ip=ip, path=self.path)
				self.hosts[ip] = new_host
				return new_host


	def check_for_host_with_ip(self, host_ip:str):
		"""
		if host exists, return the object
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"checking if host ({host_ip}) exists for this network ({self.network_address})")

			if host_ip in self.hosts:
				logger.debug(f"host ({host_ip}) exists for this network ({self.network_address})")
				return self.hosts[host_ip]

			logger.debug(f"host ({host_ip}) does not exist for this network ({self.network_address})")
			return None


	def create_host_with_ip(self, ip:str):
		"""
		creates the host; attaches it to the network obj;
		returns the list of methods to run
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"creating host ({ip}) for this network ({self.network_address})")

			new_host = Host(ip=ip, path=self.path)
			self.hosts[ip] = new_host

			# updated this object -> check for updates -> call methods
			self.check_for_updates_in_state()
			return new_host

	def get_ip_host_or_create_it(self, ip):
		"""
		gets the host object, if it exists. Otherwise, creates
		a new host object for this network. 

		checks for relevant updates in the network, if so calls the methods.
		calls the methods automatically for host when it creates it 
		"""
		# if host doesn't exist create it and get methods
		with sharedvariables.shared_lock:
			logger.debug(f'get/create host with ip ({ip})')
			host = self.check_for_host_with_ip(ip)

			if host is None: # if it doesn't exist
				logger.debug(f'Host ({ip}) didnt exist for this network {self.network_address}')

				# if it's 'our ip' in the network
				if self.our_ip == ip:
					logger.debug(f"Host ({ip}) is our IP for this network {self.network_address}")
					return None
				else:
					host = self.create_host_with_ip(ip)
					return host
			
			else:
				logger.debug(f'host ({ip}) already existed for this network returning that object')
				return host

	# PLEASE USE A LOCK
	def found_ip_host_methods(self, host:Host):
		"""
		the methods that we'll run when we find a host
		MUST RETURN A LIST
		"""
		return [host.auto]

	def reference_new_host_using_NetBIOS_hostname(self, host:Host, hostname:str):
		self.hostnames[hostname] = host
	

	def associate_netbios_workstation_to_ip_host_through_hostname(self, hostname:str, ip:str):
		"""
		checks if the IP host is already associated to a netbios workstation
		if it is:
			check if the hostname of that workstaiton is the same as the
			argument
		if not:
			check if there is already a netbios workstation with this hostname
			if exists:
				associate it with the ip host
			if no:
				create it 
				associate it with the ip host
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"associating netbios workstation ({hostname}) to Host ({ip})")
			ip_host = self.get_host_through_ip(ip)
			netbios_ws = ip_host.get_netbios_workstation_obj()

			# if host is associated with a netbios machine 
			if netbios_ws is not None:
				logger.debug(f"Host ({ip}) already had a netbios workstation obj associated")
				if netbios_ws.get_hostname() is not None and netbios_ws.get_hostname() == hostname:
					logger.debug(f"Host ({ip}) was already associated to this netbios workstation")
				else:
					logger.warning(f"Host ({ip}) is associated to a different netbios workstation")

			else: # we have to create the netbios ws
				netbios_ws = self.get_or_create_netbios_workstation_through_hostname(hostname)
				ip_host.associate_NetBIOSWorkstation(netbios_ws)
				netbios_ws.associate_host(ip_host)
			return 


	def check_if_NetBIOSWorkstation_is_associated(self, netbios_wk:NetBIOSWorkstation):
		"""
		How we check if a netbios workstation is already associated
		to this network object
		"""		
		with sharedvariables.shared_lock:
			logger.debug(f"checking if network ({self.network_address}) has the netbios workstation")
			if netbios_wk in self.netbios_workstations:
				logger.debug(f"network ({self.network_address}) has the netbios workstation")
				return True

			logger.debug(f"network ({self.network_address}) does not have the netbios workstation")
			return False


	def check_if_NetBIOSWorkstation_is_associated_through_hostname(self, hostname:str):
		"""
		Checks if the network object has a netbios workstation 
		with such a hostname.
		If it does returns the object
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"checking if network ({self.network_address}) has a netbios workstation with hostname: ({hostname})")
			for netbios_wk in self.netbios_workstations:
				if netbios_wk.hostname is not None:
					if netbios_wk.hostname == hostname:
						logger.debug(f"network ({self.network_address}) has a netbios workstation with hostname: ({hostname})")
						return netbios_wk
			logger.debug(f"network ({self.network_address}) does NOT have a netbios workstation with hostname: ({hostname})")
			return None


	def associate_NetBIOSWorkstation(self, netbios_wk:NetBIOSWorkstation):
		"""
		Associates a NetBIOSWorkstation with this network object
		we will keep it in our list of netbios workstation objects

		returns list of function 
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"associating netbios workstation to network ({self.network_address})")
			self.netbios_workstations.append(netbios_wk)
			
			# becaus we updated this object -> check for relevance 
			self.check_for_updates_in_state()
			return 


	def get_or_create_netbios_workstation_through_hostname(self, hostname:str):
		"""
		Checks if the network object has a network workstation with such 
		a hostname. If it does returns it, if it doesn't creates it, 
		associates it and returns it.
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"associating netbios workstation with hostname ({hostname}) to network ({self.network_address})")
			netbios_ws = self.check_if_NetBIOSWorkstation_is_associated_through_hostname(hostname)

			if netbios_ws != None:
				return netbios_ws

			# create the netbios workstation object
			new_netbios_ws = NetBIOSWorkstation(host = None, hostname = hostname)

			# associate the object to this network
			self.associate_NetBIOSWorkstation(new_netbios_ws)
			return new_netbios_ws



	def updateComponent(self, add_nc:AbstractNetworkComponent):
		if isinstance(add_nc, Host):
			print(f"[+] Found new Livehost {add_nc.ip} for network {self.network_address}")
			self.hosts[add_nc.ip] = add_nc
		pass


	def check_if_netbios_group_exists(self, group_name:str, _type:str):
		with sharedvariables.shared_lock:
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
		return NetBIOSGroup(group_name, group_type)

	def associate_netbios_group_to_this_network(self, group:NetBIOSGroup):
		with sharedvariables.shared_lock:
			if not self.check_if_netbios_group_exists(group.name, group.type):
				group_id = group.name+'#'+group.type
				self.netbios_groups[group_id] = group

				self.check_for_updates_in_state()
				return 
