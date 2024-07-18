import copy
from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent

from COMPONENTS.ldap.ldapserver import LdapServer
from COMPONENTS.domains.domainuser import DomainUser
from COMPONENTS.domains.domaingroup import DomainGroup


from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.domains.enumdomainsthroughrpc.method import EnumDomainsThroughRPC
from COMPONENTS.domains.enumdomainusersthroughrpc.method import EnumDomainUsersThroughRPC


class Domain(AbstractNetworkComponent):
	"""
	Defines the class for domains that we find for the network
	This domain will be inserted in a forest and may or may not 
	be the root Domain for it. 
	"""
 
	"""
	change the methods to receive the context like this
 	methods = [EnumDomainsThroughRPC, EnumDomainTrustsThroughRPC, EnumDomainUsersThroughRPC, EnumDomainGroupsThroughRPC]
  	"""
	methods = [EnumDomainsThroughRPC, EnumDomainUsersThroughRPC]
	roles = ["DC", "machine"]

	def __init__(self, domain_name:str, domain_pdc:'LdapServer'=None):
		self.domain_name = domain_name
		# the domain pdc
		self.domain_pdc = domain_pdc
		self.ldap_servers = list() # list of ldap servers (ip)
		self.msrpc_servers = list() # list of msrpc servers (ip)
		self.smb_servers = list() # list of smb servers (ip)
		self.machines = dict() # the machines that belong and their role (from roles)
  
		if domain_pdc is not None:
			self.machines[domain_pdc.get_host()] = "DC"

		self.trusts = list() # list of domain trusts
		self.users = list() # list of user objects (should be private)
		self.groups = list() # list of group objects (should be private)
  
		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)



	def get_context(self):
		"""
		get the context for this domain
		"""
		logger.debug(f"getting context for domain ({self.domain_name})")
		with sharedvariables.shared_lock:
			context = dict()
			context['domain_name'] = self.get_domain_name()
			context['domain_pdc'] = self.domain_pdc
			context['trusts'] = copy.deepcopy(self.trusts)
			context['usernames'] = copy.deepcopy(self.get_list_usernames())
			context['groupnames'] = copy.deepcopy(self.get_list_groupnames())
			context['msrpc_servers'] = copy.deepcopy(self.get_msrpc_servers())
			return context

 
	def get_list_usernames(self):
		"""
		Goes to each user known to the domain and attempts to extract the username.
		returns a list of all usernames
		"""
		with sharedvariables.shared_lock:
			list_usernames = list()
			for user in self.users: 
				username = user.get_username()
				if username is not None:
					list_usernames.append(username)
			return list_usernames

	def get_list_groupnames(self):
		"""
		Goes to each group known to the domain and attempts to extract the groupname.
		returns a list of all the groupnames
		"""
		with sharedvariables.shared_lock:
			list_groupnames = list()
			for group in self.groups:
				groupname = group.get_groupname()
				if groupname is not None:
					list_groupnames.append(groupname)
			return list_groupnames


	def get_pdc(self):
		with sharedvariables.shared_lock:
			return self.domain_pdc

	def check_domain_in_trusts(self, domain):
		with sharedvariables.shared_lock:
			if domain in self.trusts:
				return True
			return False

	def get_domain_name(self):
		return self.domain_name


	def display_json(self):
		"""
		method to retrieve the json information to display the domain
		"""
		data = dict()
		data['name'] = self.get_domain_name()
		pdc = self.get_pdc()
		if pdc is not None:
			data['PDC'] = pdc.get_host().get_ip()
   
		data['DCs'] = list()
		data['machines'] = list()
		for machine in self.machines:
			if self.machines[machine] == "DC":
				data['DCs'].append(machine.get_ip())
			data['machines'].append(machine.get_ip())
   
		data['Trusts'] = list()
		for domain in self.trusts:
			data['Trusts'].append(domain.get_domain_name())
   
		data['Users'] = list()
		for user in self.users:
			data['Users'].append(user.display_json())
	
		return data

		
	def add_dc(self, host):
		"""
		Adds a domain controller (ldap) to this domain. 
		As a domain controller we can add this to our ldap_servers. marpc_servers and smb_servers
  		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Adding dc to domain ({self.get_domain_name()})")
   
			# check if it's already in the machines of this domain
			if host not in self.machines:
				self.machines[host] = "DC"

			# if its in the list of machines but has a normal machine
			if host in self.machines:
				if self.machines[host] == "machine":
					self.machines[host] = "DC"

			# since host is DC we can add to the list of services:
			self.msrpc_servers.append(host.get_ip())
			self.ldap_servers.append(host.get_ip())
			self.smb_servers.append(host.get_ip())

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 

	def add_pdc(self, pdc:'LdapServer'):
		with sharedvariables.shared_lock:
			logger.debug(f"Adding pdc ({pdc.get_host().get_ip()}) to Domain ({self.get_domain_name()})")
			this_pdc = self.get_pdc()
			if this_pdc is None:
				logger.debug(f"Domain ({self.get_domain_name()}) had no pdc, adding now")
				self.domain_pdc = pdc
			else:
				logger.debug(f"Domain ({self.get_domain_name()}) had a pdc ({this_pdc.get_host().get_ip()})")

	def add_domain_trust(self, domain):
		with sharedvariables.shared_lock:
			logger.debug(f"Adding domain ({domain.get_domain_name()}) to domain ({self.get_domain_name()}) trusts")

			# if we already have this trust
			if self.check_domain_in_trusts(domain):
				logger.debug(f"domain ({domain.get_domain_name()}) was already in trusts")
				return []
			# otherwise
			else:
				self.trusts.append(domain)
				logger.debug(f"domain ({domain.get_domain_name()}) placed in domain trusts ({self.get_domain_name()})")
				return []

	def auto_function(self):
		"""
		The function that will call the methods and send their run events
		"automatically" for the thread that runs the commands
  		"""
    
		for method in self.methods:
			# create the events
			list_events = method.create_run_events(self.get_context())
			# for each event send it to the threrad
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		return 


	def get_or_create_user_from_username(self, username):
		"""
		Attempts to retrieve the user with this username.
		If it fails it will create a new user with this username
		"""
		with sharedvariables.shared_lock:
			# if we have the user 
			for user in self.users:
				if user.get_username() == username:
					return user

			# create the user, add it to users
			user = DomainUser(username= username, rid = None)
			self.users.append(user)

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return user


	def get_or_create_group_from_groupname(self, groupname):
		"""
		Attempts to retrieve the group with this groupname.
		If it fails it will create a new group with this groupname
		"""
		with sharedvariables.shared_lock:
			# if we have the group
			for group in self.groups:
				if group.get_groupname() == groupname:
					return group

			# create the group, add it to the groups
			group = DomainGroup(groupname= groupname, rid =None)
			self.groups.append(group)

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return group


	"""
 	MSRPC
  	"""
   
	def get_msrpc_servers(self): 
		"""
		Retrieves the list of msrpc servers 
		(the ips of the msrpc servers listed)
  		"""
		with sharedvariables.shared_lock:
			return self.msrpc_servers

	def add_msrpc_server(self, rpc_ip):
		"""
  		Adds an ip to the msrpc_servers list.
		Checks if the ip is already in the list.
    	"""
		list_msrpc_server_ips = self.get_msrpc_servers()
		if rpc_ip not in list_msrpc_server_ips:
			logger.debug(f"Adding {rpc_ip} to the list of msrpc servers of domain {self.domain_name}")
			self.msrpc_servers.append(rpc_ip)