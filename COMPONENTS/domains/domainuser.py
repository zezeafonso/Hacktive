from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread


class DomainUser(AbstractNetworkComponent):
	"""
	Defines the class for a domain user and the attributes of interest.
	"""
	methods = [] # i even doubt he will have one

	def __init__(self, username:str, rid:str=None):
		self.username = username
		self.rid = rid 
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)

	def get_context(self):
		logger.debug(f"getting context for domain user ({self.username})")
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

	def get_username(self):
		with sharedvariables.shared_lock:
			return self.username

	def get_rid(self):
		with sharedvariables.shared_lock:
			return self.rid


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