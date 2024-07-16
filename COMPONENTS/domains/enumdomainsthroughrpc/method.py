from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
from THREADS.sharedvariables import shared_lock

from COMPONENTS.domains.enumdomainsthroughrpc.filter import EnumDomainsThroughRPC_Filter
from COMPONENTS.domains.enumdomainsthroughrpc.updater import updater
from LOGGER.loggerconfig import logger


class EnumDomainsThroughRPC(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'enumdomains through rpc'
	_filename = 'outputs/rpc-enumdomains-'
	_previous_args = set()
	_filter = EnumDomainsThroughRPC_Filter
	_updater = updater

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainsThroughRPC._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"EnumDomainsThroughRPC didn't receive a context")
			return []

		if not EnumDomainsThroughRPC.check_context(context):
			return []

		with shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if EnumDomainsThroughRPC.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			EnumDomainsThroughRPC._previous_args.add(args)

		# command to run 
		#cmd = f"rpcclient -U=\"foxriver.local/DrTancredi%Password123\" {context_ip_address} -c=\'enumdomains\'"
		cmd = f"rpcclient {ip} -c=\'enumdomains\' -U=\'%\'"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = EnumDomainsThroughRPC._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=EnumDomainsThroughRPC, context=context)]

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
			logger.debug(f"context for EnumDomainsThroughRPC doesn't have an associated_object")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainsThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainsThroughRPC was already used ({arg})")
			return True 
		return False 