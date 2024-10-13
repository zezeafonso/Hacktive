from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from LOGGER.loggerconfig import logger
from COMPONENTS.network.arpscan.filter import ArpScan_Filter
from COMPONENTS.network.arpscan.updater import update_arp_scan


class ArpScan(AbstractMethod):
	_name = "arp scan"
	_filename = "outputs/arpscan"
	_previous_args = set()
	_filter = ArpScan_Filter
	_updater = update_arp_scan

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{ArpScan.name}"


	@staticmethod
	def create_run_events(context:dict=None) -> list:

		if context is None:
			logger.debug(f"ArpScan didn't receive any context")
			return []

		if not ArpScan.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			network_address = context['network_address']
			list_args = list()
			list_args.append(network_address)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if ArpScan.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			ArpScan._previous_args.add(args)

		str_network_address = str(network_address).replace('/','_')
		str_network_address = str_network_address.replace('.', '_')
		# output file
		output_file = ArpScan._filename +str_network_address +'.out'

		cmd =  f"sudo nmap -PR -sn -n {network_address}"
		return [Run_Event(type='run', filename=cmd+'.out', command=cmd, method=ArpScan,context=context)]

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
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in ArpScan._previous_args:
			logger.debug(f"arg for ArpScan was already used ({arg})")
			return True 
		return False 

	@staticmethod
	def check_context(context:dict):
		"""
		Checks if the context provided to run the method has the
		necessary values
		"""
		# it is not associated with an object
		if context['our_ip'] is None :
			logger.debug(f"context for ArpScan doesn't have our_ip")
			return False
		# if we don't have a group id for the object
		if context['network_address'] is None:
			logger.debug(f"context for ArpScan doesn't have a network_address")
			return False
		return True

