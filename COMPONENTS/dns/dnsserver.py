from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

import COMPONENTS.dns.componentupdater as componentupdater

from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent


from .zonetransfer import ZoneTransfer

class DNSServer(AbstractNetworkComponent):
	"""
	The representation of a DNS server
	"""
	string_to_class = {
		"ZoneTransfer": ZoneTransfer
	}
	methods = None

	def __init__(self, host='Host', port=str):
		self.host = host
		self.port = port # might be None
		self.domain = None # the associated domain, might be useful 
  
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
		if self.domain is not None:
			context['domain_name'] = self.domain.get_domain_name()
		else:
			host = self.host
			domain = host.get_domain()
			if domain is not None:
				context['domain_name'] = domain.get_domain_name()
				self.domain = domain
		return context


	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['DNS Server'] = dict()
			data['DNS Server']['port'] = self.port
    
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
       			DNS server @ ({self.get_ip()})")
			if self.domain is not None:
				logger.debug(f"SMB server @ ({self.get_ip()}) \
        			already has a domain")
				return 

			# associate the domain
			self.domain = domain
			# this object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 
