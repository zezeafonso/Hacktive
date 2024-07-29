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
		self.domain = None # the associated domain ( might be needed afterwards)
  
  		# we updated this object
		sharedvariables.add_object_to_set_of_updated_objects(self)
  

  
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

			return context


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
				list_events = method.create_run_events(self.get_context())
				for event in list_events:
					send_run_event_to_run_commands_thread(event)
		

	def get_auto_function(self):
		return self.auto_function

	def found_domain_methods(self):
		return [self.auto_funcion]
