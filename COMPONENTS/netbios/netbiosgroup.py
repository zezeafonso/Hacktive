import importlib
from pathlib import Path

from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.netbios.nbnsgroupmembers.method import NBNSGroupMembers



class NetBIOSGroup():
	methods = None

	def __init__(self, group_name, group_type):
		"""
		The type of the group clarifies if this is <00> or <1c>
		"""
		self.name = group_name
		self.type = group_type
		self.id = group_name.lower()+'#'+group_type
		self.associated = None # the object to which is associated (network / wins server)
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


	def get_id(self):
		with sharedvariables.shared_lock:
			return self.id

	def get_context(self):
		with sharedvariables.shared_lock:
			logger.debug(f"getting context for NetBIOSGroup ({self.name})")
			context = dict()
			context['group_name'] = self.name
			context['group_id'] = self.id
			context['associated_object'] = self.associated # might be None
		return context


	def display_json(self):
		with sharedvariables.shared_lock:
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
			list_events += method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def associate_with_object(self, obj):
		"""
		Associates this network group, with something, most likely 
		the network or subnet where we are present.
		"""
		with sharedvariables.shared_lock:
			if self.associated is not None:
				logger.debug(f"changing the associated object of netbios group ({self.id})")
			self.associated = obj

			# we updated this object
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return

