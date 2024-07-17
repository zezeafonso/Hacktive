from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables


class DomainGroup(AbstractNetworkComponent):
	"""
	Defines the class for a Domain group and the attributes of interest.
	"""
	methods = [] # I even doubt that he will have one

	def __init__(self, groupname:str, rid:str=None):
		self.groupname = groupname
		self.rid = rid # might be None

	def get_context(self):
		logger.debug(f"Getting context for Domain Group ({self.groupname})")
		return 

	def display_json(self):
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
			return 
