from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from COMPONENTS.hosts.checkifsmbserviceisrunning.filter import CheckIfSMBServiceIsRunning_Filter
from COMPONENTS.hosts.checkifsmbserviceisrunning.updater import update_check_if_smb_service_is_running
from LOGGER.loggerconfig import logger


class CheckIfSMBServiceIsRunning(AbstractMethod):
	_name = 'check if SMB service is running'
	_filename = 'outputs/nmap_port_445'
	_previous_args = set()
	_filter = CheckIfSMBServiceIsRunning_Filter
	_updater = update_check_if_smb_service_is_running

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{CheckIfSMBServiceIsRunning._name}"

	@staticmethod
	def create_run_events(context:dict) -> list:
		"""
		defines the command events for this class.
		"""
		# check for the context variables
		if context is None:
			logger.warning("No context for CheckIfSMBServiceIsRunning")
			return []

		# check for the specific requirements in context
		if not CheckIfSMBServiceIsRunning.check_context(context):
			return []

		# must be locked accessing shared memory
		with shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if CheckIfSMBServiceIsRunning.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			CheckIfSMBServiceIsRunning._previous_args.add(args)

		# get the output file name
		str_ip = str(ip).replace('.','_')
		output_file = CheckIfSMBServiceIsRunning._filename +str_ip + '.out'
		# construct the command
		cmd = f"sudo nmap -p 139,445 -n -Pn {ip}"

		# create the event 
		return [Run_Event(type='run', filename=output_file, command=cmd, method=CheckIfSMBServiceIsRunning, context=context)]

	def get_context(context):
		"""
		Nothing for now
		"""
		pass

	@staticmethod 
	def check_if_args_were_already_used(arg: tuple):
		"""
		checks if the args were already used, if so don't create the run events. 
		MUST BE USED WITH A LOCK
		"""
		if arg in CheckIfSMBServiceIsRunning._previous_args: # O(1) average
			logger.debug(f"arg for CheckIfSMBServiceIsRunning was already used ({arg})")
			return True
		return False

	@staticmethod
	def check_context(context:dict):
		"""
		checks for requirements, if we have all the information we need in the context
		"""
		if context['ip'] is None: 
			logger.debug(f"context for CheckIfSMBServiceIsRunning doesn't have an ip")
			return False
		if context['network_address'] is None:
			logger.debug(f"context for CheckIfSMBServiceIsRunning doesn't have a network address")
			return False
		if context['interface_name'] is None:
			logger.debug(f"context for CheckIfSMBServiceIsRunning doesn't have an interface name")
			return False
		return True

	@staticmethod
	def check_for_objective(context):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True

