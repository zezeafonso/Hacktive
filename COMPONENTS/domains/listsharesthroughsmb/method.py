from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.domains.listsharesthroughsmb.filter import ListSharesThroughSMB_Filter
from COMPONENTS.domains.listsharesthroughsmb.updater import ListSharesThroughSMB_Updater

from LOGGER.loggerconfig import logger


class ListSharesThroughSMB(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'list shares through smb'
	_filename = 'outputs/smb-listshares-'
	_previous_args = set()
	_filter = ListSharesThroughSMB_Filter
	_updater = ListSharesThroughSMB_Updater

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{ListSharesThroughSMB._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"ListSharesThroughSMB didn't receive a context")
			return []

		if not ListSharesThroughSMB.check_context(context):
			return []

		unused_smb_server_ips = list()
		domain_name = context['domain_name']

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			list_smb_servers_ip = context['smb_servers'] # will be a list
   
			# check if this method was already called with these arguments
			unused_smb_server_ips = list()
			for smb_server_ip in list_smb_servers_ip:
				args = [smb_server_ip, domain_name]
				t_args=tuple(args)
				if not ListSharesThroughSMB.check_if_args_were_already_used(t_args):
					unused_smb_server_ips.append(smb_server_ip)
					ListSharesThroughSMB._previous_args.add(t_args)

		list_run_events = list()
	

		# for every unused msrpc server ip 
		for ip in unused_smb_server_ips:
			# command to run 
			cmd = f"smbclient -L //{ip} -U=\'{domain_name}/%\'" # anonymous user for now

			# output file 
			str_ip_address = ip.replace('.', '_')
			output_file = ListSharesThroughSMB._filename + str_ip_address + '.out'
			list_run_events.append(Run_Event(type='run', filename=cmd+'.out', command=cmd, method=ListSharesThroughSMB, context=context))
		
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
		# it is not associated with an object
		if context['smb_servers'] is None :
			logger.debug(f"context for ListSharesThroughSMB doesn't have smb servers")
			return False
		# if we don't have a group id for the object
		if context['domain_name'] is None:
			logger.debug(f"context for ListSharesThroughSMB doesn't have a domain_name")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in ListSharesThroughSMB._previous_args:
			logger.debug(f"arg for ListSharesThroughSMB was already used ({arg})")
			return True 
		return False 
