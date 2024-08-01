from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.smb.basiccrackmapexec.filter import BasicCrackMapExec_Filter
from COMPONENTS.smb.basiccrackmapexec.updater import BasicCrackMapExec_Updater

from LOGGER.loggerconfig import logger


class BasicCrackMapExec(AbstractMethod):
	"""
	
	"""
	_name = 'list shares through smb'
	_filename = 'outputs/smb-crackmapexec_smb-'
	_previous_args = set()
	_filter = BasicCrackMapExec_Filter
	_updater = BasicCrackMapExec_Updater

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{BasicCrackMapExec._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"BasicCrackMapExec didn't receive a context")
			return []

		if not BasicCrackMapExec.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			server_ip = context['ip']
			arg = [server_ip]
			tup_arg = tuple(arg)

			# already run -> exit 
			if BasicCrackMapExec.check_if_args_were_already_used(tup_arg):
				return []
			
			# add to the list of used arguments
			BasicCrackMapExec._previous_args.add(tup_arg)

		list_run_events = list()

		cmd = f"crackmapexec smb {server_ip}" # guest user with no password 

		# output file 
		str_ip_address = server_ip.replace('.', '_')
		output_file = BasicCrackMapExec._filename + str_ip_address + '.out'
		list_run_events.append(Run_Event(type='run', filename=output_file, command=cmd, method=BasicCrackMapExec, context=context))
		
		return list_run_events
  
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
		if context['ip'] is None:
			return 
		if context['smb_server'] is None:
			return
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in BasicCrackMapExec._previous_args:
			logger.debug(f"arg for BasicCrackMapExec was already used ({arg})")
			return True 
		return False 
