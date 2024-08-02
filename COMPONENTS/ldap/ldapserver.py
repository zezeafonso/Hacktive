from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

import COMPONENTS.ldap.componentupdater as componentupdater

# methods
from COMPONENTS.ldap.queryrootdseofdcthroughldap.method import QueryRootDSEOfDCThroughLDAP
from COMPONENTS.ldap.querymetadatawindapsearch.method import QueryMetadataWindapsearch
from COMPONENTS.ldap.retrievelistofuserswithwindapsearch.method import RetrieveListUsersWithWindapsearch

class LdapServer:
	"""
	If we find that a host is in fact a ldap server.
	We want to check if it is a domain controller for active directory.
	We will check if the services of a domain controller are open.

	kerberos: 88 
	dns: 53 
	smb: 139
	msrpc: 135
	"""
	methods = [QueryRootDSEOfDCThroughLDAP, RetrieveListUsersWithWindapsearch]

	def __init__(self, host):
		self.host = host
		self.domain = None # (might be needed)
		self.supported_versions = set() # in strings
  
		logger.debug(f"Created Ldap Server for host ({host.get_ip()})")
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)


	def get_ip(self):
		with sharedvariables.shared_lock:
			return self.host.get_ip()


	def get_context(self):
		logger.debug(f"getting context for LdapServer ({self.host.get_ip()})")
		with sharedvariables.shared_lock:
			context = dict()

			context['ldap_server'] = self # reference to this object (doesn't work)
			context['ip'] = self.host.get_ip()
			context['network_address'] = self.host.get_network().get_network_address()
			context['interface_name'] = self.host.get_network().get_interface().get_interface_name()
			if self.domain is not None:
				context['domain_name'] = self.domain.get_domain_name()
			else:
				host = self.host
				domain = host.get_domain()
				if domain is not None:
					context['domain_name'] = domain.get_domain_name()
					self.domain = domain

			return context


	def get_domain(self):
		with sharedvariables.shared_lock:
			host = self.get_host()
			domain = host.get_domain()
			return domain

	def get_host(self):
		with sharedvariables.shared_lock:
			return self.host

	
	# Functions

	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['LDAP Server'] = dict()
			data['LDAP Server']['domain name'] = self.get_host().get_domain().get_domain_name()
			# supported versions (not serializable)
			data['LDAP Server']['supported versions'] = list()
			for version in self.supported_versions:
				data['LDAP Server']['supported versions'].append(version)
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.

		calls each method with context.
		"""
		for method in self.methods:
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		"""
		Call all methods when we find a domain for this ldap server
		"""
		return [self.auto_function]


	def associate_domain(self, domain):
		"""
 		Associates this server to a domain
   		"""
		componentupdater.associate_server_to_domain(domain, self)
		return 

	def add_domain(self, domain):
		"""
  		Associates a domain to this server
    	"""
		with sharedvariables.shared_lock:
			logger.debug(f"Associating domain ({domain.domain_name}) to \
       			LDAP server @ ({self.get_ip()})")
			if self.domain is not None:
				logger.debug(f"LDAP server @ ({self.get_ip()}) \
        			already has a domain")
				return 

			# associate the domain
			self.domain = domain
			# this object was updated
			sharedvariables.add_object_to_set_of_updated_objects(self)
			return 


	def add_supported_version(self, version:str):
		"""
  		Checks if the version is already present.
		If already present nothing happens.
    	"""
		with sharedvariables.shared_lock:
			logger.debug(f"adding supported version : ({version}) to \
       ldap server ({self.get_ip()})")
			if version not in self.supported_versions:
				self.supported_versions.add(version)
			return 