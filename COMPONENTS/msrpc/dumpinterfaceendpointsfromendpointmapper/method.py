from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
from THREADS.sharedvariables import shared_lock

from LOGGER.loggerconfig import logger
from COMPONENTS.msrpc.dumpinterfaceendpointsfromendpointmapper.filter import DumpInterfaceEndpointsFromEndpointMapper_Filter
from COMPONENTS.msrpc.dumpinterfaceendpointsfromendpointmapper.updater import update


class DumpInterfaceEndpointsFromEndpointMapper(AbstractMethod):
	_name = 'dump interface endpoints from endpoint mapper'
	_filename = 'outputs/rpcdump-'
	_previous_args = set()
	_filter = DumpInterfaceEndpointsFromEndpointMapper_Filter
	_updater = update
 

	def __init__(self):
		pass

	@staticmethod 
	def to_str():
		return f"{DumpInterfaceEndpointsFromEndpointMapper._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"DumpInterfaceEndpointsFromEndpointMapper didn't receive a context")
			return []

		if not DumpInterfaceEndpointsFromEndpointMapper.check_context(context):
			return []

		# must be locked accessing shared memory
		with shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if DumpInterfaceEndpointsFromEndpointMapper.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			DumpInterfaceEndpointsFromEndpointMapper._previous_args.add(args)


		# command to run 
		cmd = f"rpcdump.py {ip}"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = DumpInterfaceEndpointsFromEndpointMapper._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=DumpInterfaceEndpointsFromEndpointMapper, context=context)]

	@staticmethod
	def check_for_objective(context):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True


	@staticmethod
	def check_context(context:dict):
		"""
		Checks if the context provided to run the method has the
		necessary values
		"""
		# it is not associated with an object
		if context['ip'] is None :
			logger.debug(f"context for DumpInterfaceEndpointsFromEndpointMapper doesn't have an ip")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in DumpInterfaceEndpointsFromEndpointMapper._previous_args:
			logger.debug(f"arg for DumpInterfaceEndpointsFromEndpointMapper was already used ({arg})")
			return True 
		return False 
