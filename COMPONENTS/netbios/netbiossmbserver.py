from LOGGER.loggerconfig import logger
from THREADS.sharedvariables import shared_lock
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread


class NetBIOSMBServer:
	"""
	TODO:
	- add the method of checking if the smb is actually alive
	"""
	methods = []

	def __init__(self, host):
		self.host = host

		# the current context of the object
		self.state = None
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_context(self):
		logger.debug(f"getting context for NetBIOSSMBServer ({self.host.get_ip()})")
		return dict()

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
			data['NetBIOS SMB server'] = dict()
			return data
	

	def auto_function(self):
		"""
		The function that automatically calls every method in the 
		methods list
		"""
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)


	def found_domain_methods(self):
		return []
