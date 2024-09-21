import importlib
from pathlib import Path

from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.interface.interface import Interface
from COMPONENTS.domains.domain import Domain
from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.root.listinterfaces.method import ListInterfaces



class Root():
	"""
	The methods to be run should come from a file not hardcoded.
	"""
	methods = None

	def __init__(self):
		self.interfaces = {}
		self.path = {'root':self} # the path to this object
		self.domains = list() # empty list for the domains we find
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
						# Dynamically calculate the module path as a relative import path
						module_import_path = f"{module_name}.method"
						# Import the module dynamically
						module = importlib.import_module(module_import_path)
						# import the method class
						method_class = getattr(module, method_name)
						cls.methods.append(method_class)
					except (ModuleNotFoundError, AttributeError) as e:
						print(f"Error loading method {method_name} from {module_name}: {e}")
		

	# getters

	def get_context(self):
		logger.debug(f"getting context for Root")
		return dict


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
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def display_json(self):
		with sharedvariables.shared_lock:
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
		with sharedvariables.shared_lock:
			return self.domains

	# LOCK.
	# if new object return it 
	def attach_interface(self, interface_name:str):
		with sharedvariables.shared_lock:
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

		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)
		return new_interface


	def get_interface_or_create_it(self, interface_name:str):
		"""
		Retrieves the existing interface, if it exists, or 
		creates a new one.

		returns a dictionary with 'object' and 'methods' (in case
		of new interface)
		"""
		# if interface doesn't exist create it and get methods
		with sharedvariables.shared_lock:
			interface = self.check_for_interface_name(interface_name)
			if interface is None: # doesn't exist
				interface = self.create_interface_with_name(interface_name)
				return interface
			else:
				return interface # the correct interface object


	def check_for_domain(self, domain_name):
		with sharedvariables.shared_lock:
			logger.debug(f"checking if domain ({domain_name}) is present in root")
			for domain in self.domains:
				if domain.get_domain_name() == domain_name:
					logger.debug(f"domain ({domain.get_domain_name()}) is present")
					return domain
			logger.debug(f"domain ({domain_name}) is NOT present")
			return None

	def add_domain(self, domain:Domain):
		with sharedvariables.shared_lock:
			logger.debug(f"Adding domain ({domain.get_domain_name()}) to root")
			self.domains.append(domain)

	def get_or_create_domain(self, domain_name):
		with sharedvariables.shared_lock:
			# check if domain is there.
			domain = self.check_for_domain(domain_name)
			if domain is None:
				# create the Domain
				logger.debug(f"Creating domain ({domain_name})")
				domain = Domain(domain_name)
				logger.debug(f"Associating the domain ({domain_name}) to root")
				# check if it belongs to some forest? 
				self.add_domain(domain)
			return domain
