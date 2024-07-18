import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread
from LOGGER.loggerconfig import logger

class NetBIOSGroupPDC:
	methods = []

	def __init__(self, host, netbiosgroup):
		self.host = host
		self.group = netbiosgroup
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)


	def get_context(self):
		logger.debug(f"getting context for netBIOSGroupPDC ({self.host.get_ip()})")
		return dict()

	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['NetBIOS PDC'] = dict()
			return data

	def auto_function(self):
		"""
		for now doesn't do nothing.
		What we want it to do:
		+ call the ldapsearch for the naming contexts
		"""
		for method in self.methods:
			list_events = method.create_run_events(self, self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

