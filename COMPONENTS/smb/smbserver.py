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

		# the current context of the object
		self.state = None
		# the objects that depend on this object for the context
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_context(self):
		logger.debug(f"getting context for SMBServer ({self.host.get_ip()})")
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

