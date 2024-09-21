import importlib
from pathlib import Path

import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from LOGGER.loggerconfig import logger
from COMPONENTS.ldap.queryrootdseofdcthroughldap.method import QueryRootDSEOfDCThroughLDAP

class NetBIOSGroupDC:
    # it would be a good idea to check the DNS for LDAP as well
	methods = None

	def __init__(self, host, netbiosgroup):
		self.host = host
		self.group = netbiosgroup
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

	def get_host(self):
		with sharedvariables.shared_lock:
			return self.host

	def get_group(self):
		with sharedvariables.shared_lock:
			return self.group

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"getting context for NetBIOSGroupDC ({self.host.get_ip()})")
			context = dict()
			context['ip'] = self.host.get_ip()
			context['network_address'] = self.host.get_network().get_network_address()
			context['interface_name'] = self.host.get_interface().get_interface_name()
			return context

	def display_json(self):
		with sharedvariables.shared_lock:
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
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		pass
