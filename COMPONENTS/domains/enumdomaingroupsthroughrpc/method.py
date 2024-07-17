from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.domains.enumdomaingroupsthroughrpc.filter import EnumDomGroupsThroughRPC_Filter
from COMPONENTS.domains.enumdomaingroupsthroughrpc.updater import update_enum_domain_groups_through_rpc

from LOGGER.loggerconfig import logger

class EnumDomainGroupsThroughRPC(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'enum domain groups through rpc'
	_filename = 'outputs/rpc-enumdomgroups-'
	_previous_args = set()
	_filter = EnumDomGroupsThroughRPC_Filter
	_updater = update_enum_domain_groups_through_rpc

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainGroupsThroughRPC._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"EnumDomainGroupsThroughRPC didn't receive a context)")
			return []

		if not EnumDomainGroupsThroughRPC.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if EnumDomainGroupsThroughRPC.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			EnumDomainGroupsThroughRPC._previous_args.add(args)

		#cmd = f"rpcclient -U=\"foxriver.local/DrTancredi%Password123\" {context_ip_address} -c=\'enumdomgroups\'"
		cmd = f"rpcclient {ip} -c=\'enumdomgroups\' -U=\'%\'"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = EnumDomainGroupsThroughRPC._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=EnumDomainGroupsThroughRPC, context=context)]

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
			logger.debug(f"context for EnumDomainGroupsThroughRPC doesn't have an ip")
			return False
		# if we don't have a group id for the object
		if context['domain_name'] is None:
			logger.debug(f"context for EnumDomainGroupsThroughRPC doesn't have a domain_name")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainGroupsThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainGroupsThroughRPC was already used ({arg})")
			return True 
		return False