import copy

from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.msrpc.dumpinterfaceendpointsfromendpointmapper.method import DumpInterfaceEndpointsFromEndpointMapper

class MSRPCServer:
	"""
	If we find a host that is launching an RPC service 
	this class will represent it's server.
	The port for MSRPC is usually 
	"""
	# the methods that use rpc from domains should be launched in the domain not here.
	methods = [DumpInterfaceEndpointsFromEndpointMapper]

	def __init__(self, host='Host', port=str):
		self.host = host
		self.port = port # might be None

		self.state = None
		self.dependent_objects = list()
		self.objects_im_dependent = list()

		# this object will be dependent of host (for the domain name)
		host.add_dependent_object(self)

		self.check_for_updates_in_state()
  
	def get_ip(self):
		"""
  		retrieves the ip of this msrpc
    	calls the get_ip of the associated host
     	"""
		with sharedvariables.shared_lock:
			return self.host.get_ip()

	def get_context(self):
		logger.debug(f"getting context for MSRPCserver ({self.host.get_ip()})")
		with sharedvariables.shared_lock:
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
				domain.add_dependent_object(self)

				# get the list of usernames
				context['domain_usernames'] = copy.deepcopy(domain.get_list_usernames())
				# get list of groupnames
				context['domain_groupnames'] = copy.deepcopy(domain.get_list_groupnames())

			return context

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
			data['MSRPC Server'] = dict()
			data['MSRPC Server']['port'] = self.port
			return data

	def auto_function(self):
		"""
		The function that's responsible for calling the auto methods.
		"""
		with sharedvariables.shared_lock:
			logger.debug(f"Auto function for MSRPC server ({self.host.get_ip()}) was called")
			for method in self.methods:
				list_events = method.create_run_events(self.state)
				for event in list_events:
					send_run_event_to_run_commands_thread(event)
		

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		return [self.auto_funcion]
