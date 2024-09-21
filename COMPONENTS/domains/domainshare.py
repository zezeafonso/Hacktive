import importlib
from pathlib import Path

from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

class DomainShare(AbstractNetworkComponent):
	"""
	Defines the class for a domain user and the attributes of interest.
	"""
	methods = None # for now still none
 
	def __init__(self, domain, msrpc_server, sharename:str):
		with sharedvariables.shared_lock:
			self.domain = domain # can be None
			self.server = msrpc_server
			self.name = sharename
	
		# this object should be added to the list of updated ones
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
		# empty for now
		return dict()


	def auto_function(self):
		for method in self.methods:
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
    
	
	def display_json(self):
		data = dict()
		data['username'] = self.get_username()
		data['rid'] = self.get_rid()
		return data


	def add_domain(self, domain):
		"""
  		Associates a domain to this share. The domain will be able 
    	to access this share to launch other commands for example.
     	It might be important to know to which domain the share 
      	belongs to.
       	"""
		with sharedvariables.shared_lock:
			logger.debug(f"Adding domain ({domain}) to share ({self.name}) from server ({self.server})")
			if self.domain is not None:
				logger.debug(f"Share ({self.name}) already had a domain")
				return	
			self.domain = domain
			return 


	