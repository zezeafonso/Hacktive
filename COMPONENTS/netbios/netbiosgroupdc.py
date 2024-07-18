import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from LOGGER.loggerconfig import logger
from COMPONENTS.ldap.queryrootdseofdcthroughldap.method import QueryRootDSEOfDCThroughLDAP

class NetBIOSGroupDC:
    # it would be a good idea to check the DNS for LDAP as well
	methods = {QueryRootDSEOfDCThroughLDAP}

	def __init__(self, host, netbiosgroup):
		self.host = host
		self.group = netbiosgroup
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)

	def get_host(self):
		with sharedvariables.shared_lock:
			return self.host

	def get_group(self):
		with sharedvariables.shared_lock:
			return self.group

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"getting context for NetBIOSGroupDC ({self.host.get_ip()})")
			context = dict()
			context['ip'] = self.host.get_ip()
			context['network_address'] = self.host.get_network().get_network_address()
			context['interface_name'] = self.host.get_interface().get_interface_name()
			return context

	def display_json(self):
		with sharedvariables.shared_lock:
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
			list_events = method.create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		pass
