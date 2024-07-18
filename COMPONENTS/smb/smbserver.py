from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread


class SMBServer:
	"""
	If we find a host that is launching an SMB service 
	this class will represent it's server.
	The port for SMB will be 445 (usually)
	"""
	methods = []

	def __init__(self, host='Host', port=str):
		self.host = host
		self.shares = list() # list of shares in the SMB server
		self.port = port # might be None
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)


	def get_context(self):
		logger.debug(f"getting context for SMBServer ({self.host.get_ip()})")
		return dict()


	def display_json(self):
		with sharedvariables.shared_lock:
			data = dict()
			data['SMB Server'] = dict()
			data['SMB Server']['port'] = self.port
			data['SMB Server']['shares'] = list()
			for share in self.shares:
				data['SMB Server']['shares'].append(share.display_json())
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.
		"""
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)
		

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		return [self.auto_function]

