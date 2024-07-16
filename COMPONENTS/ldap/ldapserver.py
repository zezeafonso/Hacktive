from LOGGER.loggerconfig import logger

from THREADS.sharedvariables import shared_lock
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.ldap.queryrootdseofdcthroughldap.method import QueryRootDSEOfDCThroughLDAP

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
	methods = [QueryRootDSEOfDCThroughLDAP]

	def __init__(self, host):
		self.host = host

		self.state = None
		self.dependent_objects = list()

		self.check_for_updates_in_state()
		logger.debug(f"Created Ldap Server for host ({host.get_ip()})")

	def get_context(self):
		logger.debug(f"getting context for LdapServer ({self.host.get_ip()})")
		with shared_lock:
			context = dict()

			context['network_address'] = self.host.get_network().get_network_address()
			context['ip'] = self.host.get_ip()
			context['interface_name'] = self.host.get_network().get_interface().get_interface_name()
			context['domain_name'] = None

			# for the domain name
			host = self.host
			domain = host.get_domain()
			if domain is not None:
				context['domain_name'] = domain.get_domain_name()
				# add since we will need information from the domain object
				domain.add_dependent_object(self)
			return context

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def get_domain(self):
		with shared_lock:
			host = self.get_host()
			domain = host.get_domain()
			return domain

	def get_host(self):
		with shared_lock:
			return self.host

	
	# Functions

	def display_json(self):
		with shared_lock:
			data = dict()
			data['LDAP Server'] = dict()
			data['LDAP Server']['domain name'] = self.get_host().get_domain().get_domain_name()
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.

		calls each method with context.
		"""
		for method in self.methods:
			list_events = method.create_run_events(self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		"""
		Call all methods when we find a domain for this ldap server
		"""
		return [self.auto_function]