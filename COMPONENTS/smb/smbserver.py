from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

import COMPONENTS.smb.componentupdater as componentupdater

# methods
from COMPONENTS.smb.listshares.method import ListSharesThroughSMB
from COMPONENTS.smb.basiccrackmapexec.method import BasicCrackMapExec
from COMPONENTS.smb.spidershares.method import SpiderSharesThroughSMB


class SMBServer:
	"""
	If we find a host that is launching an SMB service 
	this class will represent it's server.
	The port for SMB will be 445 (usually)
	"""
	
	"""
	+ check for smb signing 
	+ check for smbv1 
	+ list shares
	+ spider shares
 	"""
	methods = [ListSharesThroughSMB, BasicCrackMapExec, SpiderSharesThroughSMB]

	def __init__(self, host='Host', port=str):
		self.host = host
		self.shares = list() # list of shares in the SMB server
		self.port = port # might be None
		self.domain = None # the associated domain, might be useful 
  
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)


	def get_context(self):
		logger.debug(f"getting context for SMBServer ({self.host.get_ip()})")
		context = dict()
		context['ip'] = self.host.get_ip() # the ip of host
		context['domain_name'] = self.domain

		# check if host got an associated domain (precaution)
		if context['domain_name'] is None:
			host = self.host
			domain = host.get_domain()
			if domain is not None:
				context['domain_name'] = domain.get_domain_name()
				self.domain = domain
		return context


	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['SMB Server'] = dict()
			data['SMB Server']['port'] = self.port
			data['SMB Server']['shares'] = list()
			for share in self.shares:
				data['SMB Server']['shares'].append(share.display_json())
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.
		"""
		for method in self.methods:
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		return [self.auto_function]


	def associate_domain(self, domain):
		"""
  		Associates a domain to this server
		(function in component updater)
    	"""
		componentupdater.associate_server_to_domain(domain, self)


	def add_domain(self, domain):
		"""
  		Associates a domain to this server
    	"""
		with sharedvariables.shared_lock:
			logger.debug(f"Associating domain ({domain.domain_name}) to \
       			SMB server @ ({self.get_host().get_ip()})")
			if self.domain is not None:
				logger.debug(f"SMB server @ ({self.get_host().get_ip()}) \
        			already has a domain")
				return 

			# associate the domain
			self.domain = domain
			# this object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 
