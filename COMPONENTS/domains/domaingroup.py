import importlib
from pathlib import Path

from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.domains.enumdomainusersingroupthroughrpc.method import EnumDomainUsersInGroupThroughRPC


class DomainGroup(AbstractNetworkComponent):
	"""
	Defines the class for a Domain group and the attributes of interest.
	"""
	methods = [] # I even doubt that he will have one
	#methods = []
 
	def __init__(self, domain, groupname:str, rid:str=None):
		# groupname and rid can't be None at the same time
		self.domain = domain # the domain it belongs to 
		self.groupname = groupname # might be None
		self.rid = rid # might be None
		self.users = set() # the set of users (no duplicates this way)
  
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
				cls.methods = []
				
				# Determine the current file's directory
				current_file_path = Path(__file__).parent
				class_name = cls.__name__
				methods_config = sharedvariables.methods_config.get(class_name, {}).get("methods", [])

				for method_entry in methods_config:
					module_name = method_entry["module"]
					method_name = method_entry["method"]
					
					try:
						# Dynamically calculate the module path relative to current directory
						module_relative_path = current_file_path / module_name
						module_import_path = ".".join(module_relative_path.parts)  # Convert to module path format
						
						# Import the module dynamically
						module = importlib.import_module(f"{module_import_path}.method")
						method = getattr(module, method_name)
						cls.methods.append(method)
					except (ModuleNotFoundError, AttributeError) as e:
						print(f"Error loading method {method_name} from {module_name}: {e}")


	def get_context(self):
		logger.debug(f"Getting context for Domain Group ({self.groupname})")
		context = dict()
		context['domain_name'] = self.domain.get_domain_name()
		context['msrpc_servers'] = self.domain.get_msrpc_servers()
		context['group_rid'] = self.rid
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
				if key == "domain" or key == "users":
					continue
				data[key] = value
			return data
		data = dict()
		data['groupname'] = self.get_groupname()
		data['rid'] = self.get_rid()
		return data

	def get_groupname(self):
		with sharedvariables.shared_lock:
			return self.groupname

	def get_rid(self):
		with sharedvariables.shared_lock:
			return self.rid

	def set_rid(self, rid):
		"""
		self.groupname (mandatory)
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"setting the rid ({rid}) for group ({self.groupname})")
			if self.rid != None:
				logger.debug(f"group already had rid ({self.rid})")
				return 
			self.rid = rid 
   
			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 

	
	def add_user(self, domainuser):
		"""
  		Adds a user to this group
    	"""
		with sharedvariables.shared_lock:
			# check if we have it in our users
			if domainuser in self.users:
				return 
			# add the user to our list
			self.users.add(domainuser)

			sharedvariables.add_object_to_set_of_updated_objects(self)
   
   
	def add_attribute(self, attr_name:str, attr_value:str):
		"""
  		Adds an attribute to the domain group.
		It will check if there is already one equal attribute.
		If there is does nothing.
		"""	
		with sharedvariables.shared_lock:
			# check if the attribute is there
			logger.debug(f"Adding to group attribute ({attr_name}) with value: ({attr_value})")
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
	
