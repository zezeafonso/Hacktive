from LOGGER.loggerconfig import logger
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread
import THREADS.sharedvariables as sharedvariables


from COMPONENTS.netbios.netbiosgroup import NetBIOSGroup
from COMPONENTS.netbios.netbiosgroupdc import NetBIOSGroupDC
from COMPONENTS.netbios.netbiossmbserver import NetBIOSMBServer
from COMPONENTS.netbios.netbiosgrouppdc import NetBIOSGroupPDC


class NetBIOSWorkstation:
	"""
	A Host if it has NetBIOS on and we receive output from queries
	We create the NetBIOSWorkstation.

	This NetBIOS Workstation may belong to a number of groups.
	In each group it might have a special role (Group DC, Group PDC, SMB server)

	Each of these roles is placed in a dictionary along with the group
	"""
	methods = []

	def __init__(self, host=None, hostname=None):
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
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)




	def get_hostname(self):
		with sharedvariables.shared_lock:
			return self.hostname

	def get_host(self):
		with sharedvariables.shared_lock:
			return self.host

	def get_ip(self):
		with sharedvariables.shared_lock:
			host = self.get_host()
			if host is not None:
				return host.get_ip()
			return None

	def get_groups(self):
		with sharedvariables.shared_lock:
			return [group for group in self.groups_and_roles]

	def get_context(self):
		logger.debug(f"getting context for netbios_workstation")
		return dict() # for now 
	

	# FUNCTIONS


	def display_json(self):
		with sharedvariables.shared_lock:
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
			list_events = method.create_run_events(self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		return

	def update_hostname(self, hostname:str):
		"""
		It can happen that we create the netbios workstation 
		without a hostname, depending on the filtered objects
		we receive first.
		This function updates the hostname value .
		"""
		with sharedvariables.shared_lock:
			if self.hostname is not None:
				if self.hostname != hostname:
					print("conflicting hostnames for the same machine !!")
			self.hostname = hostname

	def associate_new_group_without_roles(self, netbiosgroup):
		"""
		Associates a new group to this netbios workstation
		without roles means that we have no particular feature 
		for this workstation listed in the netbios so far.
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Associating group ({netbiosgroup.id}) without roles to NetBIOSWorkstation")
			self.groups_and_roles[netbiosgroup] = []

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)


	def check_if_belongs_to_group(self, netbiosgroup):
		"""
		checks if a groups is present inside the groups and
		roles dictionary
		"""
		with sharedvariables.shared_lock:
			return netbiosgroup in self.groups_and_roles

	def get_roles_associated_to_group(self, netbiosgroup):
		"""
		Retrives the roles associated with a group.
		The group might not be present in groups and roles
		as such we return None in that case
		"""
		with sharedvariables.shared_lock:
			if self.check_if_belongs_to_group(netbiosgroup):
				return self.groups_and_roles[netbiosgroup]
			else:
				return None

	def check_if_role_already_exists_for_group(self, netbiosgroup, role_class):
		"""
		Checks for the presence of duplicate objects of the same 
		class for a group. This behaviour should not happen and 
		this check prevents we inserting duplicates
		"""
		with sharedvariables.shared_lock:
			roles = self.get_roles_associated_to_group(netbiosgroup)
			if roles == None: # the group is not present 
				return False
			for role in roles:
				if isinstance(role, role_class):
					return True
			return False
	
	def add_new_role_to_group(self, netbiosgroup, role):
		"""
		The function that adds a role to a group in 
		groups and roles.
		Does not perform the checks of:
		the groups is present or not 
		the role is already in or not
		"""
		with sharedvariables.shared_lock:
			self.groups_and_roles[netbiosgroup].append(role)

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
   

	def create_and_associate_netbios_dc_group_role(self, netbiosgroup):
		"""
		creates the NetBIOSGroupDC and associates it to a group
		that MUST already be associated.

		checks if the NetBIOSGroupDC is already present in that 
		group.
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"associating netbios DC group role in group ({netbiosgroup.id})")

			netbios_dc = NetBIOSGroupDC(self.host, netbiosgroup)
			if not self.check_if_role_already_exists_for_group(netbiosgroup, NetBIOSGroupDC):
				self.add_new_role_to_group(netbiosgroup, netbios_dc)
				return 
			return 

	def add_pdc_role_for_group(self, netbiosgroup):
		"""
		Adds a pdc role for an existing group. 

		Checks if the role is already in that group.
		If not -> add it.
		returns methods 
		"""
		with sharedvariables.shared_lock:
			if not self.check_if_role_already_exists_for_group(netbiosgroup, NetBIOSGroupPDC):
				role = NetBIOSGroupPDC(self.host, netbiosgroup)
				self.add_new_role_to_group(netbiosgroup, role)
			return


	def add_group(self, netbiosgroup):
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
		with sharedvariables.shared_lock:
			logger.debug(f"Adding group ({netbiosgroup.id}) to NetBIOSWorkstation")
			if self.check_if_belongs_to_group(netbiosgroup):
				logger.debug(f"Group ({netbiosgroup.id}) already belonged to NetBIOSWorkstation")
				return 
			else:
				# place the group in dict without roles
				self.associate_new_group_without_roles(netbiosgroup)

				# domain controller role
				if netbiosgroup.type == '1c':
					# Found that this host might be a Domain Controller
					# add domain controller services to the host (or at least test them)
					return self.create_and_associate_netbios_dc_group_role(netbiosgroup)
				return



	def get_group_from_group_id(self, group_id:str):
		"""
		Returns the groups object that this netbios workstation belongs 
		to that possesses that group_id.
		"""
		with sharedvariables.shared_lock:
			groups = self.get_groups()
			for group in groups:
				if group.id == group_id:
					return group
			return None


	def get_netbios_group_dc_from_group(self, netbiosgroup):
		"""
		attains the netbios group dc from a group that is associated.
		"""
		with sharedvariables.shared_lock:
			if self.check_if_belongs_to_group(netbiosgroup):
				roles = self.get_roles_associated_to_group(netbiosgroup)
				for role in roles:
					if isinstance(role, NetBIOSGroupDC):
						return role
			return []


	def check_for_netbios_smb_server(self):
		"""
		Checks if this netbios workstation already is considered
		a netbios SMB server
		"""
		with sharedvariables.shared_lock:
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
		with sharedvariables.shared_lock:
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
		with sharedvariables.shared_lock:
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


	def associate_host(self, host):
		with sharedvariables.shared_lock:
			self.host = host

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return


	def add_netbios_smb_server(self):
		"""
		Add the role of netbios Smb server to this netbios workstation
		Check if it's already before
		"""
		with sharedvariables.shared_lock:
			# create the netbios smb server object
			netbios_smb_server = NetBIOSMBServer(self.host)
			# associate it to this object
			self.smb_server = netbios_smb_server

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return


	def associate_domain(self, domain):
		"""
  		Associates a domain to this object
    	"""
		# nothing for now
		return 

