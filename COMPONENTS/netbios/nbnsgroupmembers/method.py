from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from LOGGER.loggerconfig import logger
from COMPONENTS.netbios.nbnsgroupmembers.filter import NBNSGroupMembers_Filter
from COMPONENTS.netbios.nbnsgroupmembers.updater import update


class NBNSGroupMembers(AbstractMethod):
	_name = 'find the members of netbios group'
	_filename = "outputs/nmblookup-"
	_previous_args = set()
	_filter = NBNSGroupMembers_Filter
	_updater = update
	
	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{NBNSGroupMembers._name}"

	@staticmethod
	def create_run_events(context:dict) -> list:
		
		# context couldn't extract necessary fields
		if len(context) == 0:
			logger.debug(f"NBNSGroupMembers didn't receive any context")
			return []

		# check if the context has the required values
		if not NBNSGroupMembers.check_context(context):
			return []

		# must be locked accessing shared memory
		with sharedvariables.shared_lock:
			# extract the specific context for this command
			group_id = context['group_id']
			list_args = list()
			list_args.append(group_id)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if NBNSGroupMembers.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			NBNSGroupMembers._previous_args.add(args)

		# construct the command
		cmd =  f"nmblookup '{group_id}'"
		# output file
		output_file = NBNSGroupMembers._filename + group_id +'.out'

		return [Run_Event(type='run', filename=cmd+'.out', command=cmd, method=NBNSGroupMembers, context=context)]


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
		if arg in NBNSGroupMembers._previous_args:
			logger.debug(f"arg for NBNSGroupMembers was already used ({arg})")
			return True 
		return False 

	@staticmethod
	def check_context(context:dict):
		"""
		Checks if the context provided to run the method has the
		necessary values
		"""
		# it is not associated with an object
		if context['associated_object'] is None :
			logger.debug(f"context for NBNSGroupMembers doesn't have an associated_object")
			return False
		# if we don't have a group id for the object
		if context['group_id'] is None:
			logger.debug(f"context for NBNSGroupMembers doesn't have a group_id")
			return False
		return True