from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from LOGGER.loggerconfig import logger

from THREADS.sharedvariables import shared_lock

class DomainUser(AbstractNetworkComponent):
	"""
	Defines the class for a domain user and the attributes of interest.
	"""
	methods = [] # i even doubt he will have one

	def __init__(self, username:str, rid:str=None):
		self.username = username
		self.rid = rid 

	def get_context(self):
		logger.debug(f"getting context for domain user ({self.username})")
		return 

	def display_json(self):
		data = dict()
		data['username'] = self.get_username()
		data['rid'] = self.get_rid()
		return data

	def get_username(self):
		with shared_lock:
			return self.username

	def get_rid(self):
		with shared_lock:
			return self.rid


	def set_rid(self, rid:str):
		with shared_lock:
			logger.debug(f"setting the rid ({rid}) for user({self.username})")
			if self.rid != None:
				logger.debug(f"User already had rid ({self.rid})")
				return 
			self.rid = rid 
			return 