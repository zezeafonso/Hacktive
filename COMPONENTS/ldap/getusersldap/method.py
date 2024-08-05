from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from COMPONENTS.ldap.getusersldap.filter import GetUsersLdap_Filter
from COMPONENTS.ldap.getusersldap.updater import get_users_ldap_updater

from LOGGER.loggerconfig import logger

class GetUsersLdap(AbstractMethod):
	_name = "retrieve list of users through ldap with nmap"
	_filename = "outputs/list-users-nmap"
	_previous_args = set()
	_filter = GetUsersLdap_Filter
	_updater = get_users_ldap_updater

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{GetUsersLdap._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		logger.debug(f"creating run events for method: {GetUsersLdap._name}")

		if context is None:
			logger.debug(f" GetUsersLdap didn't receive any context )")
			return []

		if not GetUsersLdap.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			# check if this method was already called with these arguments
			args = tuple([ip]) # the tuple of args used 
			if GetUsersLdap.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			GetUsersLdap._previous_args.add(args)
		
  		# command
		cmd = f"sudo nmap -p 389 --script ldap-search --script-args \'ldap.qfilter=users\' {ip}"

		# output file
		str_ip_address = ip.replace('.', '_')
		output_file = GetUsersLdap._filename+'-'+str_ip_address +'.out'

		#cmd =  f"ldapsearch -H ldap://{context_ip_address} -x -s base namingcontexts"
		return [Run_Event(type='run', filename=output_file, command=cmd,method=GetUsersLdap, context=context)]

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
		if arg in GetUsersLdap._previous_args:
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
		# we should have information on the domain (through the metadata and rootdse)
		if context['domain_name'] is None:
			logger.debug(f"context for QueryRootDSEOfDCThroughLDAP doesn't have a domain")
			return 
		return True

