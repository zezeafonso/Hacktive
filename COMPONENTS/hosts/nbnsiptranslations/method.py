from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from LOGGER.loggerconfig import logger
from COMPONENTS.hosts.nbnsiptranslations.filter import NBNSIPTranslation_Filter
from COMPONENTS.hosts.nbnsiptranslations.updater import update_ip_to_host_nbns

import re

class NBNSIPTranslation(AbstractMethod):
	_name = "ip to hostname through NBNS"
	_filename = "outputs/nmblookup-A-"
	_previous_args = set()
	_filter = NBNSIPTranslation_Filter
	_updater = update_ip_to_host_nbns
 
 
	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{NBNSIPTranslation._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			# get context
			logger.debug(f"NBNSIPTranslation didn't receive a context")
			return []

		# if it doesn't have the necessary context values
		if not NBNSIPTranslation.check_context(context):
			return []

		with sharedvariables.shared_lock:
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if NBNSIPTranslation.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			NBNSIPTranslation._previous_args.add(args)

		context_ip_address = context['ip']
		str_ip_address = context_ip_address.replace('.', '_')
		# output file
		output_file = NBNSIPTranslation._filename +str_ip_address +'.out'

		cmd =  f"nmblookup -A {context_ip_address}"
		file_name = re.sub(r'[^\w\-_\.]', '_', cmd)
		return [Run_Event(type='run', filename=f"outputs/{file_name}", command=cmd, method=NBNSIPTranslation, context=context)]

	@staticmethod
	def check_for_objective(context):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True


	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		checks if the args were already used, if so don't create 
		the run events
		MUST be used with a lock.
		"""
		if arg in NBNSIPTranslation._previous_args:
			logger.debug(f"arg for NBNSIPTranslation was already used ({arg})")
			return True 
		return False

	@staticmethod
	def check_context(context:dict):
		"""
		Checks if the context provided to run the method has the
		necessary values
		"""
		# it is not associated with an object
		if context['ip'] is None :
			logger.debug(f"context for NBNSIPTranslation doesn't have an ip")
			return False
		return True

