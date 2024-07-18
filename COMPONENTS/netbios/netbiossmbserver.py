from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread


class NetBIOSMBServer:
	"""
	TODO:
	- add the method of checking if the smb is actually alive
	"""
	methods = []

	def __init__(self, host):
		self.host = host
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)


	def get_context(self):
		logger.debug(f"getting context for NetBIOSSMBServer ({self.host.get_ip()})")
		return dict()


	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['NetBIOS SMB server'] = dict()
			return data
	

	def auto_function(self):
		"""
		The function that automatically calls every method in the 
		methods list
		"""
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)


	def found_domain_methods(self):
		return []
