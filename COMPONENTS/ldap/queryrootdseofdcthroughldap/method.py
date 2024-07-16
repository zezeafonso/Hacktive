from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
from THREADS.sharedvariables import shared_lock

from COMPONENTS.ldap.queryrootdseofdcthroughldap.filter import QueryRootDSEOfDCThroughLDAP_Filter
from COMPONENTS.ldap.queryrootdseofdcthroughldap.updater import update_query_root_dse_of_dc_through_ldap

from LOGGER.loggerconfig import logger

class QueryRootDSEOfDCThroughLDAP(AbstractMethod):
	_name = "query root dse of DC through LDAP"
	_filename = "outputs/nmap-script-rootdse-LDAP"
	_previous_args = set()
	_filter = QueryRootDSEOfDCThroughLDAP_Filter
	_updater = update_query_root_dse_of_dc_through_ldap

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{QueryRootDSEOfDCThroughLDAP._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		logger.debug(f"creating run events for method: {QueryRootDSEOfDCThroughLDAP._name}")

		if context is None:
			logger.debug(f"QueryRootDSEOfDCThroughLDAP didn't receive any context )")
			return []

		if not QueryRootDSEOfDCThroughLDAP.check_context(context):
			return []

		with shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if QueryRootDSEOfDCThroughLDAP.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			QueryRootDSEOfDCThroughLDAP._previous_args.add(args)

		# command
		cmd = f"sudo nmap -Pn -n -p 389 --script=ldap-rootdse {ip}"
		#cmd =  f"ldapsearch -H ldap://{context_ip_address} -x -s base namingcontexts"

		# output file
		str_ip_address = ip.replace('.', '_')
		output_file = QueryRootDSEOfDCThroughLDAP._filename+'-'+str_ip_address +'.out'

		#cmd =  f"ldapsearch -H ldap://{context_ip_address} -x -s base namingcontexts"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=QueryRootDSEOfDCThroughLDAP, context=context)]

	@staticmethod
	def check_for_objective(context):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		with shared_lock:
			if 'domain_name' in context:
				if context['domain_name'] is not None:
					logger.debug(f"creating run events for method: {QueryRootDSEOfDCThroughLDAP._name} but we already have a domain name for this host")
					domain_name = context[domain_name]
					ip = context['ip']
					choice = input(f'we already have the domain name ({domain_name}) for host ({ip}), do you want to run method: ({QueryRootDSEOfDCThroughLDAP._name})? (y/n)')
					if choice != 'y':
						return False
			return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in QueryRootDSEOfDCThroughLDAP._previous_args:
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

