from THREADS.sharedvariables import shared_lock
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from LOGGER.loggerconfig import logger
from COMPONENTS.ldap.queryrootdseofdcthroughldap.method import QueryRootDSEOfDCThroughLDAP

class NetBIOSGroupDC:
    # it would be a good idea to check the DNS for LDAP as well
	methods = {QueryRootDSEOfDCThroughLDAP}

	def __init__(self, host, netbiosgroup):
		self.host = host
		self.group = netbiosgroup

		# the current context of this object
		self.state = None
		# the objects that depend on this object for context
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_host(self):
		with shared_lock:
			return self.host

	def get_group(self):
		with shared_lock:
			return self.group

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with shared_lock:
			logger.debug(f"getting context for NetBIOSGroupDC ({self.host.get_ip()})")
			context = dict()
			context['ip'] = self.host.get_ip()
			context['network_address'] = self.host.get_network().get_network_address()
			context['interface_name'] = self.host.get_interface().get_interface_name()
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

	def display_json(self):
		with shared_lock:
			data = dict()
			data['NetBIOS DC'] = dict()
			return data

	def auto_function(self):
		"""
		for now doesn't do anything.
		what we want it to do:
		+ call the ldapsearch for this machines
		+ find the other machines that have this group (done in the netbios group)
		"""
		for method in self.methods:
			list_events = method.create_run_events(self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		pass
