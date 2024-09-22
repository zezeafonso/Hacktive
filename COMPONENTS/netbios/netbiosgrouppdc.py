import importlib
from pathlib import Path

import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread
from LOGGER.loggerconfig import logger

from .nbnsgroupmembers import NBNSGroupMembers
from .queryrootdseofdcthroughldap import QueryRootDSEOfDCThroughLDAP

class NetBIOSGroupPDC:
	string_to_class = {
		"NBNSGroupMembers":NBNSGroupMembers, 
		"QueryRootDSEOfDCThroughLDAP": QueryRootDSEOfDCThroughLDAP
	}
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
				cls.methods = [] # initiate so it does not enter again
				
				# get the techniques for this class
				class_name = cls.__name__
				methods_config = sharedvariables.methods_config.get(class_name, {}).get("techniques", [])

				for class_entry in methods_config:
					class_name = class_entry["technique"]
					if class_name in cls.string_to_class:
						_class = cls.string_to_class[class_name]
						cls.methods.append(_class)


	def get_context(self):
		logger.debug(f"getting context for netBIOSGroupPDC ({self.host.get_ip()})")
		return dict()

	def display_json(self):
		with sharedvariables.shared_lock:
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
				send_run_event_to_run_commands_thread(event)

