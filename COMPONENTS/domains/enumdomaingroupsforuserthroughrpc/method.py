from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.domains.enumdomaingroupsforuserthroughrpc.filter import EnumDomainGroupsForUserThroughRPC_Filter
from COMPONENTS.domains.enumdomaingroupsforuserthroughrpc.updater import updateEnumDomainGroupsForUserThroughRPC
from LOGGER.loggerconfig import logger

import re


class EnumDomainGroupsForUserThroughRPC(AbstractMethod):
	"""
	Emumera the users that belong to a group through rpc 
	You will need the group name, and the ip of the msrpc server
	"""
	_name = 'enum domain groups for user through rpc'
	_filename = 'outputs/rpc-queryusergroups-'
	_previous_args = set()
	_filter = EnumDomainGroupsForUserThroughRPC_Filter
	_updater = updateEnumDomainGroupsForUserThroughRPC

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainGroupsForUserThroughRPC._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"EnumDomainsThroughRPC didn't receive a context")
			return []

		if not EnumDomainGroupsForUserThroughRPC.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			list_msrpc_servers_ip = context['msrpc_servers'] # will be a list
			user_rid = context['user_rid']

			# check if this method was already called with these arguments
			unused_args = list()
			for ip in list_msrpc_servers_ip:
				tup_args = (ip, user_rid)
				if not EnumDomainGroupsForUserThroughRPC.check_if_args_were_already_used(tup_args):
					unused_args.append(tup_args)
					EnumDomainGroupsForUserThroughRPC._previous_args.add(tup_args)

		# command to run 
		list_run_events = list()
  
		# for every unused msrpc server ip 
		for tup in unused_args:
			ip = tup[0] 
			user_rid = tup[1] # in hex
			cmd = f"rpcclient {ip} -c=\'queryusergroups {user_rid}\' -U=\'%\'"
			file_name = re.sub(r'[^\w\-_\.]', '_', cmd)

			# output file 
			str_ip_address = ip.replace('.', '_')
			output_file = EnumDomainGroupsForUserThroughRPC._filename + str_ip_address +'-'+str(user_rid)+ '.out'
			list_run_events.append(Run_Event( \
                    type='run', \
                    filename=f"outputs/{file_name}", \
                    command=cmd, \
                    method=EnumDomainGroupsForUserThroughRPC, \
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
		if context['msrpc_servers'] is None :
			logger.debug(f"context for EnumDomainGroupsForUserThroughRPC doesn't have MSRPC servers")
			return False
		if context['user_rid'] is None:
			logger.debug(f"Context for EnumDomainGroupsForUserThroughRPC doesn't have a group_rid")
			return False
		if context['domain_name'] is None:
			logger.debug(f"context for EnumDomainGroupsForUserThroughRPC doesn't have a domain name")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainGroupsForUserThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainGroupsForUserThroughRPC was already used ({arg})")
			return True 
		return False 