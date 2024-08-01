from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from COMPONENTS.ldap.querymetadatawindapsearch.filter import QueryMetadataWindapsearch_Filter
from COMPONENTS.ldap.querymetadatawindapsearch.updater import query_metadata_windapsearch_updater

from LOGGER.loggerconfig import logger

class QueryMetadataWindapsearch(AbstractMethod):
	_name = "query root dse of DC through LDAP"
	_filename = "outputs/metadata-windapsearch"
	_previous_args = set()
	_filter = QueryMetadataWindapsearch_Filter
	_updater = query_metadata_windapsearch_updater

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{QueryMetadataWindapsearch._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		logger.debug(f"creating run events for method: {QueryMetadataWindapsearch._name}")

		if context is None:
			logger.debug(f"QueryMetadataWindapsearch didn't receive any context )")
			return []

		if not QueryMetadataWindapsearch.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			# check if this method was already called with these arguments
			args = tuple([ip]) # the tuple of args used 
			if QueryMetadataWindapsearch.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			QueryMetadataWindapsearch._previous_args.add(args)

		# command
		cmd = f"windapsearch -m metadata --dc {ip}"

		# output file
		str_ip_address = ip.replace('.', '_')
		output_file = QueryMetadataWindapsearch._filename+'-'+str_ip_address +'.out'

		#cmd =  f"ldapsearch -H ldap://{context_ip_address} -x -s base namingcontexts"
		return [ Run_Event(type='run', filename=output_file, command=cmd, \
      				method=QueryMetadataWindapsearch, context=context)]

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
		if arg in QueryMetadataWindapsearch._previous_args:
			logger.debug(f"arg for QueryRootDSEOfDCThroughLDAP was already used ({arg})")
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
			logger.debug(f"context for QueryRootDSEOfDCThroughLDAP doesn't have an ip")
			return False
		return True

