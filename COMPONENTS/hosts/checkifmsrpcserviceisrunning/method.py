from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from COMPONENTS.hosts.checkifmsrpcserviceisrunning.filter import CheckIfMSRPCServiceIsRunning_Filter
from COMPONENTS.hosts.checkifmsrpcserviceisrunning.updater import update_check_if_msrpc_service_is_running

from LOGGER.loggerconfig import logger


class CheckIfMSRPCServiceIsRunning(AbstractMethod):
	_name = 'check if MSRPC service is running'
	_filename = 'outputs/nmap_port_135'
	_previous_args = set()
	_filter = CheckIfMSRPCServiceIsRunning_Filter
	_updater = update_check_if_msrpc_service_is_running

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{CheckIfMSRPCServiceIsRunning._name}"

	@staticmethod
	def create_run_events(context:dict) -> list:
		"""
		Will need the ip, the network and interface name
		"""
		if context is None:
			logger.debug(f"CheckIfMSRPCServiceIsRunning didn't received a context")
			return []
		
		if not CheckIfMSRPCServiceIsRunning.check_context(context):
			return []

		# must be locked accessing shared memory:
		with sharedvariables.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list()
			list_args.append(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if CheckIfMSRPCServiceIsRunning.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			CheckIfMSRPCServiceIsRunning._previous_args.add(args)


		# extract the specific context for this command
		ip = context['ip']
		network_address = context['network_address']
		interface_name = context['interface_name'] 

		# obter o output file com o ip do host
		str_ip = str(ip).replace('.','_')
		output_file = CheckIfMSRPCServiceIsRunning._filename +str_ip + '.out'
		# chamar o comando para listar os portos
		cmd = f"sudo nmap -p 135 -n -Pn {ip}"
		# criar o evento de run com o comando
		return [Run_Event(type='run', filename=cmd+'.out', command=cmd, method=CheckIfMSRPCServiceIsRunning, context=context)]

	@staticmethod
	def check_for_objective(context):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True

	@staticmethod 
	def check_if_args_were_already_used(arg: tuple):
		"""
		checks if the args were already used, if so don't create the run events. 
		"""
		if arg in CheckIfMSRPCServiceIsRunning._previous_args: # O(1) average
			logger.debug(f"arg for CheckIfMSRPCServiceIsRunning was already used ({arg})")
			return True
		return False

	@staticmethod
	def check_context(context:dict):
		"""
		checks for requirements, if we have all the information we need in the context
		"""
		if context['ip'] is None: 
			logger.debug(f"context for CheckIfMSRPCServiceIsRunning doesn't have an ip")
			return False
		if context['network_address'] is None:
			logger.debug(f"context for CheckIfMSRPCServiceIsRunning doesn't have a network_address")
			return False
		if context['interface_name'] is None:
			logger.debug(f"context for CheckIfMSRPCServiceIsRunning doesn't have a interface_name")
			return False
		return True
