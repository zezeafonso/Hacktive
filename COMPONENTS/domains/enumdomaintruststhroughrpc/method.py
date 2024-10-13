from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.domains.enumdomaintruststhroughrpc.filter import EnumDomainTrustsThroughRPC_Filter
from COMPONENTS.domains.enumdomaintruststhroughrpc.updater import update_enum_domain_trusts_through_rpc

from LOGGER.loggerconfig import logger

class EnumDomainTrustsThroughRPC(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'enum domains trusts through rpc'
	_filename = 'outputs/rpc-dsenumdomtrusts-'
	_previous_args = set()
	_filter = EnumDomainTrustsThroughRPC_Filter
	_updater = update_enum_domain_trusts_through_rpc

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainTrustsThroughRPC._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
	
		if context is None:
			return []
		
		if not EnumDomainTrustsThroughRPC.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if EnumDomainTrustsThroughRPC.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			EnumDomainTrustsThroughRPC._previous_args.add(args)

		# command to run 
		#cmd = f"rpcclient -U=\"foxriver.local/DrTancredi%Password123\" {ip} -c=\'dsenumdomtrusts\'"
		cmd = f"rpcclient {ip} -c=\'dsenumdomtrusts\' -U=\'%\'"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = EnumDomainTrustsThroughRPC._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=cmd+'.out', command=cmd, method=EnumDomainTrustsThroughRPC, context=context)]

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
		Checks if the context has the spefici required values
		to be run, if it doesn't don't create the run events
		"""
		if context['domain_name'] is None:
			logger.debug(f"context for EnumDomainTrustsThroughRPC doesn't have a domain_name")
			return False 
		if context['ip'] is None:
			logger.debug(f"context for EnumDomainTrustsThroughRPC doesn't have an ip")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainTrustsThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainTrustsThroughRPC was already used ({arg})")
			return True 
		return False 
