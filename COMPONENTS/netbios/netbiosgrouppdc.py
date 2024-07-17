import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread
from LOGGER.loggerconfig import logger

class NetBIOSGroupPDC:
	methods = []

	def __init__(self, host, netbiosgroup):
		self.host = host
		self.group = netbiosgroup

		# the current context for this object
		self.state = None
		# the objects that depend on this one for context
		self.dependent_objects = list()

		self.check_for_updates_in_state()


	def get_context(self):
		logger.debug(f"getting context for netBIOSGroupPDC ({self.host.get_ip()})")
		return dict()

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with sharedvariables.shared_lock:
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
			list_events = method.create_run_events(self, self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

