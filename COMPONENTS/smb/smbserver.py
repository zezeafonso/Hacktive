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
		self.smbv1 = None # not enabled
		self.signing = None # By default is True
  
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)


	def get_ip(self):
		with sharedvariables.shared_lock:
			return self.host.get_ip()


	def get_host(self):
		with sharedvariables.shared_lock:
			return self.host


	def get_context(self):
		logger.debug(f"getting context for SMBServer ({self.host.get_ip()})")
		context = dict()
		context['ip'] = self.host.get_ip() # the ip of host
		context['network_address'] = self.get_host().get_network().get_network_address()
		context['interface_name'] = self.get_host().get_interface().get_interface_name()
		context['domain_name'] = self.domain
		context['smb_server'] = self # doesn't work 

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
			data['SMB Server']['signing'] = self.signing
			data['SMB Server']['SMBv1'] = self.smbv1
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
       			SMB server @ ({self.get_ip()})")
			if self.domain is not None:
				logger.debug(f"SMB server @ ({self.get_ip()}) \
        			already has a domain")
				return 

			# associate the domain
			self.domain = domain
			# this object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 


	def update_smbv1_value(self, value):
		"""
  		Updates the value of smbv1 dialect
    	(required: True; not: False)
     	"""
		with sharedvariables.shared_lock:
			logger.debug(f"Updating the value of smbv1 enabled to \
       			({value}) @ ({self.get_ip()})")
			self.smbv1 = value
			logger.debug(f"updated value: {self.smbv1}")
			return 


	def update_signing_required_value(self, value):
		"""
  		Updates the value of SMB signing
    	(true or false)
     	"""
		with sharedvariables.shared_lock:
			logger.debug(f"Updating the value of SMB signing to \
       			({value}) @ ({self.get_ip()})")
			self.signing = value
			return 
