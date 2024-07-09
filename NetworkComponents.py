import copy
import queue
import threading 
import multiprocessing

import SpecificExceptions as SE
import Methods
from AbstractClasses import AbstractNetworkComponent
import ThreadShares as TS
from Events import Run_Event
from LoggingConfig import logger


def throw_run_event_to_command_listener(event:Run_Event) -> None:
	TS.cmd_queue.put(event)
	pass


"""
class Forest(AbstractNetworkComponent):
	#Defines the class for Forests of Domains

	def __init__(self, root_domain_name:str, root_domain_dc:'LdapServer'):
		self.root_name = root_domain_name
		self.root_dc = root_domain_dc
"""

class DomainGroup(AbstractNetworkComponent):
	"""
	Defines the class for a Domain group and the attributes of interest.
	"""
	methods = [] # I even doubt that he will have one

	def __init__(self, groupname:str, rid:str=None):
		self.groupname = groupname
		self.rid = rid # might be None

	def get_context(self):
		return 

	def display_json(self):
		data = dict()
		data['groupname'] = self.get_groupname()
		data['rid'] = self.get_rid()
		return data

	def get_groupname(self):
		with TS.shared_lock:
			return self.groupname

	def get_rid(self):
		with TS.shared_lock:
			return self.rid

	def set_rid(self, rid):
		"""
		self.groupname (mandatory)
		"""
		with TS.shared_lock:
			logger.debug(f"setting the rid ({rid}) for group ({self.groupname})")
			if self.rid != None:
				logger.debug(f"group already had rid ({self.rid})")
				return 
			self.rid = rid 
			return 




class DomainUser(AbstractNetworkComponent):
	"""
	Defines the class for a domain user and the attributes of interest.
	"""
	methods = [] # i even doubt he will have one

	def __init__(self, username:str, rid:str=None):
		self.username = username
		self.rid = rid 

	def get_context(self):
		return 

	def display_json(self):
		data = dict()
		data['username'] = self.get_username()
		data['rid'] = self.get_rid()
		return data

	def get_username(self):
		with TS.shared_lock:
			return self.username

	def get_rid(self):
		with TS.shared_lock:
			return self.rid


	def set_rid(self, rid:str):
		with TS.shared_lock:
			logger.debug(f"setting the rid ({rid}) for user({self.username})")
			if self.rid != None:
				logger.debug(f"User already had rid ({self.rid})")
				return 
			self.rid = rid 
			return 








class Domain(AbstractNetworkComponent):
	"""
	Defines the class for domains that we find for the network
	This domain will be inserted in a forest and may or may not 
	be the root Domain for it. 
	"""
	methods = []

	def __init__(self, domain_name:str, domain_pdc:'LdapServer'=None):
		self.domain_name = domain_name
		# the domain pdc
		self.domain_pdc = domain_pdc
		# list of domain controllers
		self.domain_dcs = list()
		if domain_pdc is not None:
			self.domain_dcs.append(domain_pdc) # add the PDC also 

		self.trusts = list() # list of domain trusts
		self.users = list() # list of user objects (should be private)
		self.groups = list() # list of group objects (should be private)


		# the current context
		self.state = None
		# the objects that depend on this one for context
		# - the hosts that belongs to this domain
		# - the forest to which this domain will belong
		self.dependent_objects = []

		self.check_for_updates_in_state()



	def get_context(self):
		"""
		get the context for this domain
		"""
		context = dict()
		context['domain_name'] = self.get_domain_name
		context['domain_pdc'] = self.domain_pdc
		context['domain_dcs'] = copy.deepcopy(self.domain_dcs)
		context['trusts'] = copy.deepcopy(self.trusts)
		context['usernames'] = copy.deepcopy(self.get_list_usernames())
		context['groupnames'] = copy.deepcopy(self.get_list_groupnames())
		return context

	def get_list_usernames(self):
		"""
		Goes to each user known to the domain and attempts to extract the username.
		returns a list of all usernames
		"""
		with TS.shared_lock:
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
		with TS.shared_lock:
			list_groupnames = list()
			for group in self.groups:
				groupname = group.get_groupname()
				if groupname is not None:
					list_groupnames.append(groupname)
			return list_groupnames

	def add_dependent_object(self, obj):
		"""
		Adds a dependent object.
		A dependent object is an object that uses information from this one object, to know if he can launch a new method or if he knows more information that it needs.

		calls the check_for_updates_in_state for the object appended.
		"""
		with TS.shared_lock:
			logger.debug(f"Adding object ({obj}) to list of dependent objects for this domain ({self.domain_name})")
			if obj in self.dependent_objects:
				logger.debug(f"Object ({obj}) already in list of dependent objects")
				return 

			# put the object in dependent objects
			self.dependent_objects.append(obj)
			# call its check for updates so he can see this information
			obj.check_for_updates_in_state()



	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()

			# if state changed
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for our methods
				self.auto_function()
			return 


	def get_pdc(self):
		with TS.shared_lock:
			return self.domain_pdc

	def check_domain_in_trusts(self, domain):
		with TS.shared_lock:
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
		print(self.domain_dcs)
		for dc in self.domain_dcs:
			data['DCs'].append(dc.get_host().get_ip())
		data['Trusts'] = list()
		for domain in self.trusts:
			data['Trusts'].append(domain.get_domain_name())

		data['Users'] = list()
		for user in self.users:
			data['Users'].append(user.display_json())
		return data

		
	def add_dc(self, dc:'LdapServer'):
		with TS.shared_lock:
			logger.debug("Adding dc to domain (self.domain_name")
			if dc not in self.domain_dcs:
				self.domain_dcs.append(dc)
				logger.debug(f"Added ldap server ({dc.get_host().get_ip()}) to domain ({self.get_domain_name()}) DC's")

				self.check_for_updates_in_state()
				return

	def add_pdc(self, pdc:'LdapServer'):
		with TS.shared_lock:
			logger.debug(f"Adding pdc ({pdc.get_host().get_ip()}) to Domain ({self.get_domain_name()})")
			this_pdc = self.get_pdc()
			if this_pdc is None:
				logger.debug(f"Domain ({self.get_domain_name()}) had no pdc, adding now")
				self.domain_pdc = pdc
			else:
				logger.debug(f"Domain ({self.get_domain_name()}) had a pdc ({this_pdc.get_host().get_ip()})")

	def add_domain_trust(self, domain):
		with TS.shared_lock:
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
		for method in self.methods:
			list_events = method.create_run_events(self, self.state)
			for event in list_events:
				throw_run_event_to_command_listener(event)


	def get_or_create_user_from_username(self, username):
		"""
		Attempts to retrieve the user with this username.
		If it fails it will create a new user with this username
		"""
		with TS.shared_lock:
			# if we have the user 
			for user in self.users:
				if user.get_username() == username:
					return user

			# create the user, add it to users
			user = DomainUser(username= username, rid = None)
			self.users.append(user)

			# new state
			self.check_for_updates_in_state()
			return user


	def get_or_create_group_from_groupname(self, groupname):
		"""
		Attempts to retrieve the group with this groupname.
		If it fails it will create a new group with this groupname
		"""
		with TS.shared_lock:
			# if we have the group
			for group in self.groups:
				if group.get_groupname() == groupname:
					return group

			# create the group, add it to the groups
			group = DomainGroup(groupname= groupname, rid =None)
			self.groups.append(group)

			# new state
			self.check_for_updates_in_state()
			return group



class NetBIOSGroupDC:
	methods = {Methods.QueryRootDSEOfDCThroughLDAP}

	def __init__(self, host:'Host', group:'NetBIOSGroup'):
		self.host = host
		self.group = group

		# the current context of this object
		self.state = None
		# the objects that depend on this object for context
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_host(self):
		with TS.shared_lock:
			return self.host

	def get_group(self):
		with TS.shared_lock:
			return self.group

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with TS.shared_lock:
			context = dict()
			context['ip'] = self.host.get_ip()
			context['network_address'] = self.host.get_network().get_network_address()
			context['interface_name'] = self.host.get_interface().get_interface_name()
			return context

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['NetBIOS DC'] = dict()
			return data

	def auto_function(self):
		"""
		for now doesn't do anything.
		what we want it to do:
		+ call the ldapsearch for this machines
		+ find the other machines that have this group (done in the netbios group)
		"""
		for method in self.methods:
			list_events = method.create_run_events(self, self.get_context())
			for event in list_events:
				throw_run_event_to_command_listener(event)
		pass

class NetBIOSGroupPDC:
	methods = []

	def __init__(self, host:'Host', group:'NetBIOSGroup'):
		self.host = host
		self.group = group

		# the current context for this object
		self.state = None
		# the objects that depend on this one for context
		self.dependent_objects = list()

		self.check_for_updates_in_state()


	def get_context(self):
		return dict()

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['NetBIOS PDC'] = dict()
			return data

	def auto_function(self):
		"""
		for now doesn't do nothing.
		What we want it to do:
		+ call the ldapsearch for the naming contexts
		"""
		for method in self.methods:
			list_events = method.create_run_events(self, self.get_context())
			for event in list_events:
				throw_run_event_to_command_listener(event)



class NetBIOSMBServer:
	"""
	TODO:
	- add the method of checking if the smb is actually alive
	"""
	methods = []

	def __init__(self, host:'Host'):
		self.host = host

		# the current context of the object
		self.state = None
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_context(self):
		return dict()

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['NetBIOS SMB server'] = dict()
			return data
	

	def auto_function(self):
		"""
		The function that automatically calls every method in the 
		methods list
		"""
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self, self.state)
			for event in list_events:
				throw_run_event_to_command_listener(event)

	def found_domain_methods(self):
		return []




class SMBServer:
	"""
	If we find a host that is launching an SMB service 
	this class will represent it's server.
	The port for SMB will be 445 (usually)
	"""
	methods = []

	def __init__(self, host='Host', port=str):
		self.host = host
		self.shares = list() # list of shares in the SMB server
		self.port = port # might be None

		# the current context of the object
		self.state = None
		# the objects that depend on this object for the context
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_context(self):
		return dict()

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['SMB Server'] = dict()
			data['SMB Server']['port'] = self.port
			data['SMB Server']['shares'] = list()
			for share in self.shares:
				data['SMB Server']['shares'].append(share.display_json())
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.
		"""
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self, self.state)
			for event in list_events:
				throw_run_event_to_command_listener(event)
		

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		return [self.auto_function]



class MSRPCServer:
	"""
	If we find a host that is launching an RPC service 
	this class will represent it's server.
	The port for MSRPC is usually 
	"""
	methods = [Methods.DumpInterfaceEndpointsFromEndpointMapper, 
				Methods.EnumDomainsThroughRPC, Methods.EnumDomainTrustsThroughRPC,
				Methods.EnumDomainUsersThroughRPC, Methods.EnumDomainGroupsThroughRPC]

	def __init__(self, host='Host', port=str):
		self.host = host
		self.port = port # might be None

		self.state = None
		self.dependent_objects = list()
		self.objects_im_dependent = list()

		# this object will be dependent of host (for the domain name)
		host.add_dependent_object(self)

		self.check_for_updates_in_state()

	def get_context(self):
		with TS.shared_lock:
			context = dict()

			context['network_address'] = self.host.get_network().get_network_address()
			context['ip'] = self.host.get_ip()
			context['interface_name'] = self.host.get_network().get_interface().get_interface_name()
			context['domain_name'] = None

			# for the domain name
			host = self.host
			domain = host.get_domain()
			if domain is not None:
				context['domain_name'] = domain.get_domain_name()
				domain.add_dependent_object(self)

				# get the list of usernames
				context['domain_usernames'] = copy.deepcopy(domain.get_list_usernames())
				# get list of groupnames
				context['domain_groupnames'] = copy.deepcopy(domain.get_list_groupnames())

			return context

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['MSRPC Server'] = dict()
			data['MSRPC Server']['port'] = self.port
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.
		"""
		with TS.shared_lock:
			logger.debug(f"Auto function for MSRPC server ({self.host.get_ip()}) was called")
			for method in self.methods:
				list_events = method.create_run_events(self, self.state)
				for event in list_events:
					throw_run_event_to_command_listener(event)
		

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		return [self.auto_funcion]



class LdapServer:
	"""
	If we find that a host is in fact a ldap server.
	We want to check if it is a domain controller for active directory.
	We will check if the services of a domain controller are open.

	kerberos: 88 
	dns: 53 
	smb: 139
	msrpc: 135
	"""
	methods = []

	def __init__(self, host:'Host'):
		self.host = host

		self.state = None
		self.dependent_objects = list()

		self.check_for_updates_in_state()
		logger.debug(f"Created Ldap Server for host ({host.get_ip()})")

	def get_context(self):
		with TS.shared_lock:
			context = dict()

			context['network_address'] = self.host.get_network().get_network_address()
			context['ip'] = self.host.get_ip()
			context['interface_name'] = self.host.get_network().get_interface().get_interface_name()
			context['domain_name'] = None

			# for the domain name
			host = self.host
			domain = host.get_domain()
			if domain is not None:
				context['domain_name'] = domain.get_domain_name()
				# add since we will need information from the domain object
				domain.add_dependent_object(self)
			return context

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def get_domain(self):
		with TS.shared_lock:
			host = self.get_host()
			domain = host.get_domain()
			return domain

	def get_host(self):
		with TS.shared_lock:
			return self.host

	def get_context(self):
		context = dict()
		context['ip'] = self.host.get_ip()
		context['network_address'] = self.host.get_network().get_network_address()
		context['interface_name'] = self.host.get_network().get_interface().get_interface_name()
		context['domain_name'] = self.get_domain()
		return context

	
	# Functions

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['LDAP Server'] = dict()
			data['LDAP Server']['domain name'] = self.get_host().get_domain().get_domain_name()
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.

		calls each method with context.
		"""
		for method in self.methods:
			list_events = method.create_run_events(self, self.state)
			for event in list_events:
				throw_run_event_to_command_listener(event)

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		"""
		Call all methods when we find a domain for this ldap server
		"""
		return [self.auto_function]









class NetBIOSWorkstation:
	"""
	A Host if it has NetBIOS on and we receive output from queries
	We create the NetBIOSWorkstation.

	This NetBIOS Workstation may belong to a number of groups.
	In each group it might have a special role (Group DC, Group PDC, SMB server)

	Each of these roles is placed in a dictionary along with the group
	"""
	methods = []

	def __init__(self, host:'Host'=None, hostname:str=None):
		"""
		Constructor of NetBIOSWorkstation. 
		Although (invidually) host and hostname can be None.
		They can't be both None, otherwise there is no way of 
		identifying this workstation correctly throughout the program.
		"""
		if host is None and hostname is None:
			logger.warning("Trying to create a NetBIOSWorkstation without host and hostname")
			return []
		self.host = host # can be None
		self.hostname = hostname # can be None
		self.groups_and_roles = dict() # group_name : [role1, role2]
		self.smb_server = None

		self.state = None # the current state of the context
		# the objects that depend on this object
		# HOST depends for the hostname
		self.dependent_objects = list()
		if host is not None:
			self.dependent_objects.append(host)

		# call the automatic methods
		self.check_for_updates_in_state()




	def get_hostname(self):
		with TS.shared_lock:
			return self.hostname

	def get_host(self):
		with TS.shared_lock:
			return self.host

	def get_ip(self):
		with TS.shared_lock:
			host = self.get_host()
			if host is not None:
				return host.get_ip()
			return None

	def get_groups(self):
		with TS.shared_lock:
			return [group for group in self.groups_and_roles]

	def get_context(self):
		return dict() # for now 

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	

	# FUNCTIONS


	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['NetBIOSWorkstation'] = dict()
			data['NetBIOSWorkstation']['hostname'] = self.get_hostname()
			data['NetBIOSWorkstation']['ip'] = self.get_ip()
			data['NetBIOSWorkstation']['Groups'] = dict()
			for group in self.groups_and_roles:
				data['NetBIOSWorkstation']['Groups'][group.get_id()] = dict()
				for role in self.get_roles_associated_to_group(group):
					data['NetBIOSWorkstation']['Groups'][group.get_id()] = role.display_json()
			return data

	def auto_function(self):
		# call the automatic methods
		for method in self.methods:
			list_events = method.create_run_events(self)
			for event in list_events:
				throw_run_event_to_command_listener(event)
		return

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
			logger.debug(f"Associating group ({group.id}) without roles to NetBIOSWorkstation")
			self.groups_and_roles[group] = []

			self.check_for_updates_in_state()
			return

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

			# updates this object -> check for updates -> call methods
			self.check_for_updates_in_state()

	def create_and_associate_netbios_dc_group_role(self, group:'NetBIOSGroup'):
		"""
		creates the NetBIOSGroupDC and associates it to a group
		that MUST already be associated.

		checks if the NetBIOSGroupDC is already present in that 
		group.
		"""
		with TS.shared_lock:
			logger.debug(f"associating netbios DC group role in group ({group.id})")

			netbios_dc = NetBIOSGroupDC(self.host, group)
			if not self.check_if_role_already_exists_for_group(group, NetBIOSGroupDC):
				self.add_new_role_to_group(group, netbios_dc)
				return 
			return 

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
			return


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
			logger.debug(f"Adding group ({group.id}) to NetBIOSWorkstation")
			if self.check_if_belongs_to_group(group):
				logger.debug(f"Group ({group.id}) already belonged to NetBIOSWorkstation")
				return 
			else:
				# place the group in dict without roles
				self.associate_new_group_without_roles(group)

				# domain controller role
				if group.type == '1c':
					return self.create_and_associate_netbios_dc_group_role(group)
				return



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


	def check_for_netbios_smb_server(self):
		"""
		Checks if this netbios workstation already is considered
		a netbios SMB server
		"""
		with TS.shared_lock:
			logger.debug(f"checking if netbios workstation has a SMB server")
			if self.smb_server is not None:
				logger.debug(f"netbios workstation has a SMB server")
				return True

			logger.debug(f"netbios workstation does not have a SMB server")
			return False


	def associate_netbios_smb_server(self, netbios_smb_server:NetBIOSMBServer):
		"""
		associates a netbios smb server to this netbios workstation
		"""
		with TS.shared_lock:
			logger.debug(f"associating smb server to this netbios workstation")
			self.smb_server = netbios_smb_server


	def get_function_methods_for_netbios_smb_server(self, smb_server):
		return smb_server.auto


	def get_netbios_smb_server_or_create_it(self):
		"""
		checks for an smb server associated to this netbios workstation
		object. If it is associated returns the object. Otherwise 
		creates, associates and return the new object and methods.
		"""
		with TS.shared_lock:
			logger.debug(f"getting or creating a NetBIOS SMB server for netbios workstation")
			if self.check_for_netbios_smb_server():
				logger.debug(f"netbios workstation had a NetBIOS SMB server associated")
				return {'object':self.smb_server, 'methods':[]}

			if self.host is None:
				logger.warning("trying to create a NetBIOS SMB server for a NetBIOS workstation that doesn't have a host")

			logger.debug(f"Creating new NetBIOS SMB server for NetBIOS workstation")
			netbios_smb_server = NetBIOSMBServer(self.host)
			methods = [self.get_function_methods_for_netbios_smb_server(netbios_smb_server)]
			return {'object':netbios_smb_server, 'methods':methods}


	def associate_host(self, host:'Host'):
		with TS.shared_lock:
			self.host = host

			# udpated object -> check for updates -> call methods
			self.check_for_updates_in_state()
			return 


	def add_netbios_smb_server(self):
		"""
		Add the role of netbios Smb server to this netbios workstation
		Check if it's already before
		"""
		with TS.shared_lock:
			# create the netbios smb server object
			netbios_smb_server = NetBIOSMBServer(self.host)
			# associate it to this object
			self.smb_server = netbios_smb_server

			self.check_for_updates_in_state()
			return


	def found_domain_methods(self):
		return []


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
	#methods = {Methods.PortScan._name: Methods.PortScan}
	methods = [Methods.NBNSIPTranslation, Methods.CheckIfMSRPCServiceIsRunning, Methods.CheckIfSMBServiceIsRunning]
	
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
		self.DNS_hostname = None
		self.fqdn = None
		self.AD_domain_roles = dict() # {domain_obj: role} - > the role might be None, 'DC' or 'PDC'
		self.roles = dict() # class_name: obj - > ex: 'NetBIOSWorkstation':nw_obj; 'LdapServer'
		self.ports = dict()

		# the current state of the network component
		self.state = None # it starts as an empty dict
		# the list of objects that depend on the host
		self.dependent_objects = list() 

		# call the automatic methods first time
		self.check_for_updates_in_state()

	# getters

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with TS.shared_lock:
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

	def add_dependent_object(self, obj):
		with TS.shared_lock:
			self.dependent_objects.append(obj)

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 


	def get_netbios_workstation_obj(self):
		with TS.shared_lock:
			logger.debug(f"getting netbios workstaion obj from Host ({self.ip})")

			if self.check_if_host_has_netbios_workstation_role():
				return self.roles['NetBIOSWorkstation']
			else:
				logger.debug(f"Host ({self.ip}) had no netbios workstation machine associated")
			return None

	def get_msrpc_server_obj(self):
		with TS.shared_lock:
			if self.check_if_host_has_rpc_server_role():
				return self.roles['MSRPCServer']
			return None

	def get_ldap_server_obj(self):
		with TS.shared_lock:
			logger.debug(f"Getting the ldap server for host ({self.get_ip()})")
			if 'ldap server' not in self.roles:
				logger.debug(f"Host ({self.get_ip()}) didn't have a ldap server")
				return None
			return self.roles['ldap server']

	def get_netbios_hostname(self):
		"""
		checks if the host has the netbios workstation role
		checks if the netbios workstation object has a hostname
		returns the hostname
		"""
		with TS.shared_lock:
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
		with TS.shared_lock:
			if len(self.AD_domain_roles) != 0:
				domain_list = list(self.AD_domain_roles.keys())
				return domain_list[0] # only the first (and only) element
			return None

	def get_ip(self):
		with TS.shared_lock:
			return self.ip

	def get_root(self):
		with TS.shared_lock:
			return self.path['root']

	def get_interface(self):
		with TS.shared_lock:
			return self.path['interface']

	def get_network(self):
		with TS.shared_lock:
			return self.path['network']

	def get_host(self):
		with TS.shared_lock:
			return self.path['host']

	

	"""
	Functions
	"""
				

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['Host'] = dict()
			data['Host']['ip'] = self.get_ip()
			data['Host']['hostname'] = self.get_netbios_hostname()
			data['Host']['roles'] = list()
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
			list_events = method.create_run_events(self, self.get_context())
			for event in list_events:
				throw_run_event_to_command_listener(event)
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


	def found_dc_methods(self):
		"""
		the methods for when we find a dc
		"""
		dc_methods = [Methods.QueryRootDSEOfDCThroughLDAP]
		for method in dc_methods:
			list_events = method.create_run_events(self)
			for event in list_events:
				throw_run_event_to_command_listener(event)
		
	def found_hostname_methods(self, hostname:str):
		"""
		the methods for when we found a hostname
		"""
		return [] # for now


	def add_role_ldap_server(self):
		"""
		adds a ldap server role to this host.
		"""
		with TS.shared_lock:
			logger.debug(f"Adding a ldap server role to this host ({self.get_ip()})")

			ldap_server = LdapServer(self)
			self.roles['ldap server'] = ldap_server

			self.check_for_updates_in_state()
			return ldap_server

	def get_or_add_role_ldap_server(self):
		"""
		If this host already has a role of ldap server returns the 
		ldap server object. Otherwise, creates and associates a new one
		"""
		with TS.shared_lock:
			ldap_server = self.get_ldap_server_obj()
			if ldap_server is None:
				ldap_server = self.add_role_ldap_server()
				
			return ldap_server


	# NETBIOS

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


	def associate_NetBIOSWorkstation(self, netbios_workstation:NetBIOSWorkstation):
		"""
		associates the netbios workstaiton to this host, 
		returns the automatic methods for the netbios workstation

		Updates the NetBIOSWorkstation object to point to this host
		as well
		"""
		with TS.shared_lock:
			logger.debug(f"Associating netbios workstation to Host ({self.ip})")
			self.roles['NetBIOSWorkstation'] = netbios_workstation

			# because we updated the object -> check for updates -> call methods
			self.check_for_updates_in_state()
			return

	def check_if_host_has_netbios_workstation_role(self):
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
			netbios_ws = self.get_netbios_workstation_obj()
			if netbios_ws is None:
				self.add_role_netbios_workstation(hostname=None)
				netbios_ws = self.get_netbios_workstation_obj()
			netbios_ws.add_group(netbios_group) # empty list of list with auto functions

			self.check_for_updates_in_state()
		return



	# SMB

	def check_if_host_has_smb_server_role(self):
		with TS.shared_lock:
			logger.debug(f"Checking if host ({self.ip}) has a smb server role")
			if 'SMBServer' not in self.roles:
				logger.debug(f"Host ({self.ip}) does not have a smb server role")
				return False
			logger.debug(f"Host ({self.ip}) has a smb server role")
			return True


	def get_or_add_role_smb_server(self, port=str):
		"""
		Add and SMB server role to the host.
		First checks if it already has
		"""
		with TS.shared_lock:
			logger.debug(f"Host ({self.ip}) adding smb server role")

			if self.check_if_host_has_smb_server_role():
				logger.debug(f"Host ({self.ip}) already had a smb server role")
				return self.roles['SMBServer'] 
			else:
				smb_server_obj = SMBServer(self, port)
				self.roles['SMBServer'] = smb_server_obj

				# updated this object -> call methods (if case)
				self.check_for_updates_in_state()
				return smb_server_obj


	def found_smb_service_running_on_port(self, port=str):
		with TS.shared_lock:
			smb_server = self.get_or_add_role_smb_server(port)
			return smb_server



	# RPC


	def check_if_host_has_rpc_server_role(self):
		with TS.shared_lock:
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
		with TS.shared_lock:
			logger.debug(f"Host ({self.ip}) adding rpc server role")

			if self.check_if_host_has_rpc_server_role():
				logger.debug(f"host ({self.ip}) already has a rpc server role")
				return self.roles['MSRPCServer']
			else:
				msrpc_server = MSRPCServer(self, port)
				self.roles['MSRPCServer'] = msrpc_server
				logger.debug(f"Added MSRPC server role to ({self.ip})")

				self.check_for_updates_in_state()
				return msrpc_server


	def found_msrpc_service_running_on_port(self, port):
		with TS.shared_lock:
			msrpc_server = self.get_or_add_role_rpc_server(port)
			return msrpc_server




	# Domains

	def add_ldap_server_to_domain_dependent_objects(self):
		"""
		Adds the ldap server of this host to the domain list of dependent objects.

		This way when the domain is updated the ldap-server will receive a 'notification', and can check for it's relevant values
		"""
		with TS.shared_lock:
			if 'ldap_server' in self.roles and self.get_domain() is not None:
				domain = self.get_domain()
				domain.add_dependent_object(self.roles['ldap_server'])
			return 


	def add_msrpc_server_to_domain_dependent_objects(self):
		"""
		Adds the MSRPC server of this host to the domain list of dependent objects.

		This way when the domain is updated the ldap-server will receive a 'notification', and can check for it's relevant values.
		"""
		with TS.shared_lock:
			if 'MSRPCServer' in self.roles and self.get_domain() is not None:
				domain = self.get_domain()
				domain.add_dependent_object(self.roles['MSRPCServer'])
			return 


	def associate_domain_to_host_if_not_already(self, domain:Domain):
		"""
		+ Checks if it has a domain associated
		+ (if not) adds this new domain to the dictionary
		+ gives the role of None (machine) to the roles

		calls methods if it was updated
		"""
		with TS.shared_lock:
			logger.debug(f"associating domain ({domain.get_domain_name()}) to host ({self.get_ip()})")

			associated_domain = self.get_domain()
			if associated_domain is not None:
				logger.debug(f"Host ({self.get_ip()}) is already associated to a domain ({associated_domain.get_domain_name()})")
				return 

			self.AD_domain_roles[domain] = None # only machine level for now
			logger.debug(f"associated domain ({domain.get_domain_name()}) to host ({self.get_ip()}) successfully")

			# the host is dependent on information from the domain
			domain.add_dependent_object(self)
			# msrpc and ldap are also dependent on information from the domain
			self.add_msrpc_server_to_domain_dependent_objects()
			self.add_ldap_server_to_domain_dependent_objects()

			# we updated this object (added a new dependency)
			self.check_for_updates_in_state()
			return 

	def associate_DC_role_to_associated_domain(self, domain:Domain):
		with TS.shared_lock:
			logger.debug(f"associating role DC to host's ({self.get_ip()}) associated domain")
			domain = self.get_domain()

			# if not associated to any domain
			if domain is None:
				logger.debug(f"Host ({self.get_ip()}) was not associated to a domain")
				return 
			# if it's already a PDC or DC
			if self.AD_domain_roles[domain] is not None and self.AD_domain_roles[domain] == 'PDC':
				return 

			self.AD_domain_roles[domain] = 'DC' # hard coded

	def associate_PDC_role_to_associated_domain(self, domain:Domain):
		with TS.shared_lock:
			logger.debug(f"associating role PDC to host's ({self.get_ip()}) associated domain")
			domain = self.get_domain()
			if domain is None:
				logger.debug(f"Host ({self.get_ip()}) was not associated to a domain")

			self.AD_domain_roles[domain] = 'PDC' # hard coded


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
		with TS.shared_lock:
			auto_functions = list()
			auto_functions += [self.found_domain_methods]
	
			# call the specific methods for each
			for role_name in self.roles:
				role_obj = self.roles[role_name]
				auto_functions += role_obj.found_domain_methods()
			return auto_functions




class NetBIOSGroup():
	methods = [Methods.NBNSGroupMembers]

	def __init__(self, group_name, group_type):
		"""
		The type of the group clarifies if this is <00> or <1c>
		"""
		self.name = group_name
		self.type = group_type
		self.id = group_name.lower()+'#'+group_type
		self.associated = None # the object to which is associated (network / wins server)

		# the current context of the object
		self.state = None
		# the objects that depend on this object for context
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_id(self):
		with TS.shared_lock:
			return self.id

	def get_context(self):
		context = dict()
		context['group_name'] = self.name
		context['group_id'] = self.id
		context['associated_object'] = self.associated # might be None
		return context

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['NetBIOSGroup'] = dict()
			data['NetBIOSGroup']['id'] = self.id
			return data

	def add_group_member(self):
		"""
		Function to add a group member to a netBIOS group
		this way we can also get the member through here
		"""
		pass

	def auto_function(self):
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
		list_events = []
		for method in self.methods:
			list_events += method.create_run_events(self, self.state)
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
					logger.debug(f"changing the associated object of netbios group ({self.id})")
				self.associated = obj

				self.check_for_updates_in_state()
				return






class Network(AbstractNetworkComponent):
	"""
	to add:
	- get the dns server for it

	"""
	methods = {Methods.ArpScan}
	
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
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
			n_a = self.network_address
		return n_a

	def get_our_ip(self):
		return self.our_ip

	def get_host_through_ip(self, ip):
		with TS.shared_lock:
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
		with TS.shared_lock:
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
			list_events = method.create_run_events(self, self.get_context())
			for event in list_events:
				throw_run_event_to_command_listener(event)

	def add_our_ip(self, ip:str):
		with TS.shared_lock:
			self.our_ip = ip

			# because we update the object -> check for relevance
			self.check_for_updates_in_state()
			return 

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


	def check_for_host_with_ip(self, host_ip:str):
		"""
		if host exists, return the object
		"""
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		with TS.shared_lock:
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
		return NetBIOSGroup(group_name, group_type)

	def associate_netbios_group_to_this_network(self, group:NetBIOSGroup):
		with TS.shared_lock:
			if not self.check_if_netbios_group_exists(group.name, group.type):
				group_id = group.name+'#'+group.type
				self.netbios_groups[group_id] = group

				self.check_for_updates_in_state()
				return 




class Interface(AbstractNetworkComponent):
	"""
	add: 
	- dhcp broadcast discover 
	- responder analyzer (more on this later)
	"""
	methods = {}

	def __init__(self, interface_name:str, path:dict):
		self.interface_name = interface_name
		self.networks = {}
		self.path = path.copy()
		self.path['interface'] = self

		self.state = None # Corresponds to the (present) context)
		# the list of objects that depend on the state of this one
		# No one depends on the interface
		self.dependent_objects = list() 

		# will call the automatic methods
		self.check_for_updates_in_state()

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with TS.shared_lock:
			context = dict()
			context['interface_name'] = self.get_interface_name()
			return context 

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			# first run: context != None
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 



	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['interface'] = dict()
			data['interface']['name'] = self.interface_name
			data['interface']['networks'] = list()
			for network_name in self.networks:
				data['interface']['networks'].append(self.networks[network_name].display_json())
			return data

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
		with TS.shared_lock:
			if network_name in self.networks:
				return self.networks[network_name]
		return None

	def create_network_with_network_str(self, network_name:str):
		"""
		creates the network; attaches it to the interface obj;
		returns the list of methods to run
		"""
		with TS.shared_lock:
			new_network = Network(network_name, self.path) 
			self.networks[network_name] = new_network

			# because we updated this object -> check for relevance
			self.check_for_updates_in_state()
			return new_network

	def get_network_or_create_it(self, network_str):
		"""
		USER INPUT - must choose if we want to add new network

		retrieves the network object with network_str, if 
		it exists for this interface. Otherwise, creates a new 
		object network.

		If the network didn't exist. We will ask the user if 
		he wants to keep it as a network component

		returns: dict with 'object' and 'methods' (if we created a 
		new network obj)
		"""
		# if network doesn't exist create it and get methods
		with TS.shared_lock:
			network = self.check_for_network_str(network_str)
			if network == None: # doesn't exist
				# create the network, but first ask if we want it 
				choice = input(f"[I]: add network ({network_str})? (y/n)")
				# ASK THE USER IF THIS NETWORK IS THE ONE
				if choice == 'yes' or choice == 'y':
					# checks for updates as well
					network = self.create_network_with_network_str(network_str)
					return network
				else:
					return None
			else: # it exists
				return network

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

	"""
	Run this when we find a new interface
	"""
	def auto_function(self):
		# no need for lock, the methods don't change
		for method in self.methods:
			list_events = method.create_run_events(self, self.state)
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
		self.domains = list() # empty list for the domains we find

		# this will be the current state of the context 
		# for now is None, because we haven't once checked for it.
		self.state = None 
		# the objects that depend on the root for context
		self.dependent_objects = list()

	# getters

	def get_context(self):
		return dict

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 


	def get_root(self):
		return self.path['root']

	# Functions
	def auto_function(self, banner:str = 'console >'):
		"""
		Calls each method that is present in the list of methods with the 
		current state of the object.
		"""
		# no need for lock, the methods don't change
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self, self.get_context())
			for event in list_events:
				throw_run_event_to_command_listener(event)

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['interfaces'] = list()
			for _int in self.interfaces:
				interface = self.interfaces[_int]
				data['interfaces'].append(interface.display_json())
				#data['interface'] = interface.display_json()
			data['domains'] = list()
			for domain in self.domains:
				data['domains'].append(domain.display_json())
			return data

	def add_interface(self, interface:Interface):
		# call the methods from the interface
		self.interfaces[interface.interface_name] = interface

	def get_domains(self) -> list:
		with TS.shared_lock:
			return self.domains

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
			return self.interfaces[interface_name]
		return None

	def create_interface_with_name(self, interface_name:str):
		"""
		creates the interface; attaches it to the root obj;
		returns the list of methods to run
		"""
		new_interface = Interface(interface_name, self.path)
		self.interfaces[interface_name] = new_interface

		# because we updated the object -> check for relevance
		self.check_for_updates_in_state()
		return new_interface

	def found_interface_methods(self, interface:Interface):
		"""
		the methods that we'll run when we find a interface
		MUST BE A LIST
		"""
		return [interface.auto]


	def get_interface_or_create_it(self, interface_name:str):
		"""
		Retrieves the existing interface, if it exists, or 
		creates a new one.

		returns a dictionary with 'object' and 'methods' (in case
		of new interface)
		"""
		# if interface doesn't exist create it and get methods
		with TS.shared_lock:
			interface = self.check_for_interface_name(interface_name)
			if interface is None: # doesn't exist
				interface = self.create_interface_with_name(interface_name)
				return interface
			else:
				return interface # the correct interface object
		

	# TODO: do with lock
	def updateComponent(self, nc_to_add:AbstractNetworkComponent):
		if isinstance(nc_to_add, Interface):
			print(f"Found new interface: {nc_to_add.interface_name} with networks: {nc_to_add.networks}")
			self.add_interface(nc_to_add)
		else:
			raise SE.NoUpdateComponentForThatClass()


	def check_for_domain(self, domain_name):
		with TS.shared_lock:
			logger.debug("checking if domain ({domain.get_domain_name()}) is present in root")
			for domain in self.domains:
				if domain.get_domain_name() == domain_name:
					logger.debug(f"domain ({domain.get_domain_name()}) is present")
					return domain
			logger.debug(f"domain ({domain_name}) is NOT present")
			return None

	def add_domain(self, domain:Domain):
		with TS.shared_lock:
			logger.debug(f"Adding domain ({domain.get_domain_name()}) to root")
			self.domains.append(domain)

	def get_or_create_domain(self, domain_name):
		with TS.shared_lock:
			# check if domain is there.
			domain = self.check_for_domain(domain_name)
			if domain is None:
				# create the Domain
				domain = Domain(domain_name=domain_name)
				# check if it belongs to some forest? 
				self.add_domain(domain)
			return domain



