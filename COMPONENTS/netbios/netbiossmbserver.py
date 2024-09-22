import importlib
from pathlib import Path

from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from .nbnsgroupmembers import NBNSGroupMembers
from .queryrootdseofdcthroughldap import QueryRootDSEOfDCThroughLDAP


class NetBIOSMBServer:
	"""
	TODO:
	- add the method of checking if the smb is actually alive
	"""
	string_to_class = {
		"NBNSGroupMembers":NBNSGroupMembers, 
		"QueryRootDSEOfDCThroughLDAP": QueryRootDSEOfDCThroughLDAP
	}
	methods = None

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
