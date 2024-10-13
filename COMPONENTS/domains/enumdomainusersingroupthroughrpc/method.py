from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.domains.enumdomainusersingroupthroughrpc.filter import EnumDomainUsersInGroupThroughRPC_Filter
from COMPONENTS.domains.enumdomainusersingroupthroughrpc.updater import updateEnumDomainUsersInGroupThroughRPC
from LOGGER.loggerconfig import logger

import re
class EnumDomainUsersInGroupThroughRPC(AbstractMethod):
	"""
	Emumera the users that belong to a group through rpc 
	You will need the group name, and the ip of the msrpc server
	"""
	_name = 'enum domain users in group through rpc'
	_filename = 'outputs/rpc-querygroupmem-'
	_previous_args = set()
	_filter = EnumDomainUsersInGroupThroughRPC_Filter
	_updater = updateEnumDomainUsersInGroupThroughRPC

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainUsersInGroupThroughRPC._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"EnumDomainsThroughRPC didn't receive a context")
			return []

		if not EnumDomainUsersInGroupThroughRPC.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			list_msrpc_servers_ip = context['msrpc_servers'] # will be a list
			msrpc_group = context['group_rid']
    
			# check if this method was already called with these arguments
			unused_args = list()
			for ip in list_msrpc_servers_ip:
				tup_args = (ip, msrpc_group)
				if not EnumDomainUsersInGroupThroughRPC.check_if_args_were_already_used(tup_args):
					unused_args.append(tup_args)
					EnumDomainUsersInGroupThroughRPC._previous_args.add(tup_args)

		# command to run 
		list_run_events = list()
  
		# for every unused msrpc server ip 
		for tup in unused_args:
			ip = tup[0] 
			group_rid = tup[1] # in hex
			cmd = f"rpcclient {ip} -c=\'querygroupmem {group_rid}\' -U=\'%\'"
			file_name = re.sub(r'[^\w\-_\.]', '_', cmd)

			# output file 
			str_ip_address = ip.replace('.', '_')
			output_file = EnumDomainUsersInGroupThroughRPC._filename + str_ip_address +'-'+str(group_rid)+ '.out'
			list_run_events.append(Run_Event(type='run', filename=f"outputs/{file_name}", command=cmd, method=EnumDomainUsersInGroupThroughRPC, context=context))
   
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
		if context['msrpc_servers'] is None :
			logger.debug(f"context for EnumDomainsThroughRPC doesn't have MSRPC servers")
			return False
		if context['group_rid'] is None:
			logger.debug(f"Context for EnumDomainUsersinGroupThroughRPC doesn't have a group_rid")
			return False
		if context['domain_name'] is None:
			logger.debug(f"context for EnumDomainUsersInGroupThroughRPC doesn't have a domain name")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainUsersInGroupThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainsThroughRPC was already used ({arg})")
			return True 
		return False 