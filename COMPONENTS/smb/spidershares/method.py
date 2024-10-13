from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.smb.spidershares.filter import SpiderSharesThroughSMB_Filter
from COMPONENTS.smb.spidershares.updater import SpiderSharesThroughSMB_Updater

from LOGGER.loggerconfig import logger


class SpiderSharesThroughSMB(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'spider shares through smb'
	_filename = 'outputs/smb-spidershares-'
	_previous_args = set()
	_filter = SpiderSharesThroughSMB_Filter
	_updater = SpiderSharesThroughSMB_Updater

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{SpiderSharesThroughSMB._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"SpiderSharesThroughSMB didn't receive a context")
			return []

		if not SpiderSharesThroughSMB.check_context(context):
			return []

		unused_ips = list()


		with sharedvariables.shared_lock:
			# extract the specific context for this command
			server_ip = context['ip']
			arg = [server_ip]
			tup_arg = tuple(arg)
			if SpiderSharesThroughSMB.check_if_args_were_already_used(tup_arg):
				return []
			ip = server_ip
			# remember used argument
			SpiderSharesThroughSMB._previous_args.add(tup_arg)

		list_run_events = list()

		# command to run (guest account, list until depth 100)
		cmd = f"smbmap -u guest -p '' -H {ip} -r --depth 100 --no-banner"
		
		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = SpiderSharesThroughSMB._filename + str_ip_address + '.out'
		list_run_events.append(\
			Run_Event(type='run', \
				filename=cmd+'.out', \
				command=cmd, \
				method=SpiderSharesThroughSMB, \
				context=context))
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
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in SpiderSharesThroughSMB._previous_args:
			logger.debug(f"arg for ListSharesThroughSMB was already used ({arg})")
			return True 
		return False 
