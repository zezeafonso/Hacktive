import copy
import importlib
from pathlib import Path
from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent

from COMPONENTS.ldap.ldapserver import LdapServer
from COMPONENTS.domains.domainuser import DomainUser
from COMPONENTS.domains.domaingroup import DomainGroup


from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.domains.enumdomainsthroughrpc.method import EnumDomainsThroughRPC
from COMPONENTS.domains.enumdomainusersthroughrpc.method import EnumDomainUsersThroughRPC
from COMPONENTS.domains.enumdomaingroupsthroughrpc.method import EnumDomainGroupsThroughRPC
from COMPONENTS.domains.listsharesthroughsmb.method import ListSharesThroughSMB

from .enumdomaingroupsforuserthroughrpc import EnumDomainGroupsForUserThroughRPC
from .enumdomaingroupsthroughrpc import EnumDomainGroupsThroughRPC
from .enumdomainsthroughrpc import EnumDomainsThroughRPC
from .enumdomaintruststhroughrpc import EnumDomainTrustsThroughRPC
from .enumdomainusersingroupthroughrpc import EnumDomainUsersInGroupThroughRPC
from .enumdomainusersthroughrpc import EnumDomainUsersThroughRPC
from .retrievedomainsidthroughrpc import RetrieveDomainSIDThroughRPC


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
	string_to_class = {
     	"EnumDomainsThroughRPC": EnumDomainsThroughRPC, 
    	"EnumDomainUsersThroughRPC": EnumDomainUsersThroughRPC,
     	"EnumDomainGroupsThroughRPC": EnumDomainGroupsThroughRPC,
      	"EnumDomainTrustsThroughRPC": EnumDomainTrustsThroughRPC, 
       	"EnumDomainUsersInGroupThroughRPC": EnumDomainUsersInGroupThroughRPC,
        "EnumDomainGroupsForUserThroughRPC": EnumDomainGroupsForUserThroughRPC,
        "RetrieveDomainSIDThroughRPC": RetrieveDomainSIDThroughRPC,
    }
	methods = None
	roles = ["DC", "machine"]

	def __init__(self, domain_name:str, domain_pdc:'LdapServer'=None):
		self.domain_name = domain_name
		# the domain pdc
		self.domain_pdc = domain_pdc
		self.sid = None # will be a string

		# list of interesting servers
		self.ldap_servers = list() # list of ldap servers (ip)
		self.msrpc_servers = list() # list of msrpc servers (ip)
		self.smb_servers = list() # list of smb servers (ip)
		self.dns_servers = list()
  
		#self.machines = dict() # the machines that belong and their role (from roles)

		self.machines = dict() # 'ip': obj
		self.dcs = dict() # 'ip': obj
  
		if domain_pdc is not None:
			self.dcs[domain_pdc.get_host().get_ip()] = domain_pdc.get_host()
			#self.machines[domain_pdc.get_host()] = "DC"

		self.trusts = list() # list of domain trusts
		self.users = list() # list of user objects (should be private)
		self.groups = list() # list of group objects (should be private)
  
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
			context['smb_servers'] = copy.deepcopy(self.get_smb_servers())
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

	def get_sid(self):
		with sharedvariables.shared_lock:
			return self.sid

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
		with sharedvariables.shared_lock:
			data = dict()
			data['name'] = self.get_domain_name()
			pdc = self.get_pdc()
			if pdc is not None:
				data['PDC'] = pdc.get_host().get_ip()
	
			data['DCs'] = list()
			data['machines'] = list()
			for ip in self.machines:
				data['machines'].append(ip)
			for ip in self.dcs:
				data['DCs'].append(ip)
	
			data['Trusts'] = list()
			for domain in self.trusts:
				data['Trusts'].append(domain.get_domain_name())
	
			data['Users'] = list()
			for user in self.users:
				data['Users'].append(user.display_json())
	
			data['Groups'] = list()
			for group in self.groups:
				data['Groups'].append(group.display_json())
		
			return data


	def add_host_services(self, host):
		"""
  		Checks for the relevant services of a host and adds them 
		to the list of servers.
  		"""
		with sharedvariables.shared_lock:
			ip = host.get_ip()
			# if host has ldap server and is not already present
			if host.get_ldap_server_obj() is not None:
				if ip not in self.ldap_servers:
					self.ldap_servers.append(ip)
			# if host has smb server and is not already present
			if host.get_smb_server_obj() is not None:
				if ip not in self.smb_servers:
					logger.debug(f"Adding ip ({ip}) to list of \
         				smb_servers in domain ({self.domain_name})")
					self.smb_servers.append(ip)
			# if host has rpc server and is not already present
			if host.get_msrpc_server_obj() is not None:
				if ip not in self.msrpc_servers:
					logger.debug(f"Adding ip ({ip}) to list of \
         				msrpc_servers in domain ({self.domain_name})")
					self.msrpc_servers.append(ip)
			# if host has dns server and is not already present
			if host.get_dns_server_obj() is not None:
				if ip not in self.dns_servers:
					logger.debug(f"Adding ip ({ip}) to list of \
         				dns_servers in domain ({self.domain_name})")
					self.dns_servers.append(ip)

	def add_host(self, host):
		"""
  		Adds a host to this domain.
    	Check if is already in the list of machines or DC's.
     	If not then also add it's services.
      	"""
		with sharedvariables.shared_lock:
			logger.debug(f"Adding host ({host.get_ip()}) to \
       			domain ({self.get_domain_name()})")
   
			# check if it's already in the list of hosts for this domain
			ip = host.get_ip()
			print(f'BEFORE: ip: {ip}, domain {id(self)}, machines: {self.machines}')
			if ip not in self.machines:
				logger.debug(f"Host ({ip}) was not in domain.")
				# debug:
				string = f"domain machines: "
				for ip in self.machines:
					string += f"{ip}"
				logger.debug(string)

				# add to the domain
				self.machines[ip] = host
				print(f'AFTER: ip: {ip}, domain {id(self)}, machines: {self.machines}')
			else:
				logger.debug(f"Host ({ip}) was already part of list of domain machines.")
				return

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 
		
	
	def add_dc_services(self, host_dc):
		"""
  		Adds the services of a DC host to the domain's list of
    	servers.
     	"""
		with sharedvariables.shared_lock:
			# since host is DC we can add to the list of services:
			self.msrpc_servers.append(host_dc.get_ip())
			self.ldap_servers.append(host_dc.get_ip())
			self.smb_servers.append(host_dc.get_ip())
   
			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 
  
	def add_dc(self, host):
		"""
		Adds the host to the list of DC's of the domain
  		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Adding dc to domain ({self.get_domain_name()})")
   
			# check if it's already in the machines of this domain
			ip = host.get_ip()
			if ip not in self.dcs:
				logger.debug(f"Host ({ip}) was not in domain DCs")
				if ip in self.machines:
					logger.debug(f"Host ({ip}) was listed as a normal machine in domain")
					logger.debug(f"removing Host ({ip}) from machines of domain.")
					# remove from machines
					self.machines.pop(ip) 
				# debug:
				string = f"domain machines: "
				for ip in self.machines:
					string += f"{ip}"
				logger.debug(string)
				string = f"domain DCs: "
				for ip in self.dcs:
					string += f"{ip})"
				logger.debug(string)

				# add to the list of dc
				self.dcs[ip] = host
			else:
				return 

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
			user = DomainUser(domain=self, username= username, rid = None)
			self.users.append(user)

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return user

	def get_or_create_user_from_rid(self, user_rid):
		"""
  		Retrieves the user with this rid.
    	Or (if no one found) creates one with this rid
     	"""
		with sharedvariables.shared_lock:
			# if we have the user
			for user in self.users:
				if user.get_rid() == user_rid:
					return user

			# create the user, add it to users
			user = DomainUser(domain=self, username=None, rid=user_rid)
			self.users.append(user)

			# notify that this object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return user


	def get_or_create_group_from_rid(self, group_rid):
		"""
  		Retrieves the group with this rid.
    	Or (if no one found) creates one with this rid
     	"""
		with sharedvariables.shared_lock:
			# if we have the user
			for group in self.groups:
				if group.get_rid() == group_rid:
					return group

			# create the user, add it to users
			group = DomainGroup(domain=self, groupname=None, rid=group_rid)
			self.groups.append(group)
   
			# notify that this object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return group


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
			group = DomainGroup(domain=self, groupname= groupname, rid =None)
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
			with sharedvariables.shared_lock:
				self.msrpc_servers.append(rpc_ip)	
			sharedvariables.add_object_to_set_of_updated_objects(self)
		return

	def add_domain_sid(self, sid):
		with sharedvariables.shared_lock:
			if self.get_sid() is None:
				self.sid = sid
   
   
	"""
 	DNS
  	"""
   
	def get_dns_servers(self): 
		"""
		Retrieves the list of msrpc servers 
		(the ips of the msrpc servers listed)
  		"""
		with sharedvariables.shared_lock:
			return self.dns_servers

	def add_dns_server(self, dns_ip):
		"""
  		Adds an ip to the msrpc_servers list.
		Checks if the ip is already in the list.
    	"""
		list_dns_server_ips = self.get_dns_servers()
		if dns_ip not in list_dns_server_ips:
			logger.debug(f"Adding {dns_ip} to the list of dns servers of domain {self.domain_name}")
			with sharedvariables.shared_lock:
				self.dns_servers.append(dns_ip)	
			sharedvariables.add_object_to_set_of_updated_objects(self)
		return
	
	"""
 	smb
  	"""
   
   
	def get_smb_servers(self):
		"""
  		Retrieves the list of smb servers
    	(the ips of the smb servers listed)
     	"""
		with sharedvariables.shared_lock:
			return self.smb_servers


	def add_smb_server(self, smb_ip):
		"""
  		Adds an ip to the smb_servers list
    	Checks if the ip is already in the list
     	"""
		list_smb_server_ips = self.get_smb_servers()
		if smb_ip not in list_smb_server_ips:
			logger.debug(f"Adding {smb_ip} to the list of smb servers of domain {self.domain_name}")
			with sharedvariables.shared_lock:
				self.smb_servers.append(smb_ip)
			sharedvariables.add_object_to_set_of_updated_objects(self)
		return 


	"""
 	ldap
  	"""
	def get_ldap_servers(self):
		"""
  		Retrieves the list of ldap servers
    	(the ips of the ldap servers listed)
     	"""
		with sharedvariables.shared_lock:
			return self.ldap_servers


	def add_ldap_server(self, ldap_ip):
		"""
  		Adds an ip to the ldap_servers list
    	Checks if the ip is already in the list
     	"""
		list_ldap_server_ips = self.get_smb_servers()
		if ldap_ip not in list_ldap_server_ips:
			logger.debug(f"Adding {ldap_ip} to the list of ldap servers of domain {self.domain_name}")
			with sharedvariables.shared_lock:
				self.ldap_servers.append(ldap_ip)
			sharedvariables.add_object_to_set_of_updated_objects(self)
		return 
