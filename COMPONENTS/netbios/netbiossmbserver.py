from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread


class NetBIOSMBServer:
	"""
	TODO:
	- add the method of checking if the smb is actually alive
	"""
	methods = []

	def __init__(self, host):
		self.host = host
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
		logger.debug(f"getting context for NetBIOSSMBServer ({self.host.get_ip()})")
		return dict()


	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['NetBIOS SMB server'] = dict()
			return data
	

	def auto_function(self):
		"""
		The function that automatically calls every method in the 
		methods list
		"""
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)


	def found_domain_methods(self):
		return []
