import importlib
from pathlib import Path

from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.domains.retrieveuserinformationthroughrpc.method import RetrieveUserInformationThroughRPC
from COMPONENTS.domains.enumdomaingroupsforuserthroughrpc.method import EnumDomainGroupsForUserThroughRPC

from .enumdomaingroupsforuserthroughrpc import EnumDomainGroupsForUserThroughRPC
from .enumdomaingroupsthroughrpc import EnumDomainGroupsThroughRPC
from .enumdomainsthroughrpc import EnumDomainsThroughRPC
from .enumdomaintruststhroughrpc import EnumDomainTrustsThroughRPC
from .enumdomainusersingroupthroughrpc import EnumDomainUsersInGroupThroughRPC
from .enumdomainusersthroughrpc import EnumDomainUsersThroughRPC



class DomainUser(AbstractNetworkComponent):
	"""
	Defines the class for a domain user and the attributes of interest.
	"""
	string_to_class = {
     	"EnumDomainsThroughRPC": EnumDomainsThroughRPC, 
    	"EnumDomainUsersThroughRPC": EnumDomainUsersThroughRPC,
     	"EnumDomainGroupsThroughRPC": EnumDomainGroupsThroughRPC,
      	"EnumDomainTrustsThroughRPC": EnumDomainTrustsThroughRPC, 
       	"EnumDomainUsersInGroupThroughRPC": EnumDomainUsersInGroupThroughRPC,
        "EnumDomainGroupsForUserThroughRPC": EnumDomainGroupsForUserThroughRPC
    }
	methods = None

	def __init__(self, domain, username:str=None, rid:str=None):
		# username and rid can't be both None
		self.domain = domain # the associated domain
		self.username = username # sAMAccountName, can be None
		self.rid = rid # can be None
		self.groups = set() # the set of groups to which the user belongs to
		self.distinguished_name = None
		self.user_principal_name = None 
  
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
		logger.debug(f"Getting context for Domain user (username: {self.username} rid {self.rid})")
		context = dict()
		context['domain_name'] = self.domain.get_domain_name()
		context['msrpc_servers'] = self.domain.get_msrpc_servers() # ips
		context['user_rid'] = self.rid
		context['username'] = self.username 
		return context

	def auto_function(self):
		for method in self.methods:
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			for key, value in self.__dict__.items():
				if key == "domain" or key == "groups":
					continue
				data[key] = value
			return data
		#data['username'] = self.get_username()
		#data['rid'] = self.get_rid()
		#data['user principal name'] = self.get_user_principal_name()
		#data['distinguished name'] = self.get_distinguished_name()
		return data

	def get_username(self):
		with sharedvariables.shared_lock:
			return self.username

	def get_rid(self):
		with sharedvariables.shared_lock:
			return self.rid

	def get_user_principal_name(self):
		with sharedvariables.shared_lock:
			return self.user_principal_name

	def get_distinguished_name(self):
		with sharedvariables.shared_lock:
			return self.distinguished_name


	def set_rid(self, rid:str):
		with sharedvariables.shared_lock:
			logger.debug(f"setting the rid ({rid}) for user({self.username})")
			if self.rid != None:
				logger.debug(f"User already had rid ({self.rid})")
				return 
			self.rid = rid 

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 


	def add_group(self, domaingroup):
		"""
		Checks if the user already has a record of this domaingroup.
  		Adds a domaingroup to the the groups this user belongs to
		"""
		with sharedvariables.shared_lock:
			if domaingroup in self.groups:
				return 

			# add this group to the set of groups
			self.groups.add(domaingroup)
			
			# notify that this object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return


	def add_distinguished_name(self, distinguished_name:str):
		with sharedvariables.shared_lock:
			logger.debug(f"Adding distinguished name ({distinguished_name})\
	   to user ({self.username})")
			if self.distinguished_name is not None:
				logger.debug(f"User already had a distinguished name")
				return 

			self.distinguished_name = distinguished_name
			logger.debug(f"New distinguished name ({distinguished_name}) set.")
			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 
				
	
	def add_user_principal_name(self, user_principal_name:str):
		with sharedvariables.shared_lock:
			logger.debug(f"Adding user principal name ({user_principal_name})\
	   to user ({self.username})")
			if self.user_principal_name is not None:
				logger.debug(f"User already had a user principal name")
				return 

			self.user_principal_name = user_principal_name
			logger.debug(f"New user principal name ({user_principal_name}) set.")
			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 


	def add_attribute(self, attr_name:str, attr_value:str):
		"""
  		Adds an attribute to the domain user.
		It will check if there is already one equal attribute.
		If there is does nothing.
		"""	
		with sharedvariables.shared_lock:
			# check if the attribute is there
			logger.debug(f"Adding to user attribute ({attr_name}) with \
	   value: ({attr_value})")
			if hasattr(self, attr_name):
				attr = getattr(self, attr_name)
				# if it has value
				if attr is not None:
					logger.debug(f"Domain user already had attribute: ({attr_name}) with value: ({attr})")
				else:
					setattr(self, attr_name, attr_value)
					logger.debug(f"Set attribute ({attr_name}) with value: ({attr_value})")
			else:
				setattr(self, attr_name, attr_value)
				logger.debug(f"Created and set attribute ({attr_name}) with value: ({attr_value})")
			
