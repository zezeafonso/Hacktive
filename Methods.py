import queue

from Events import Run_Event

from AbstractClasses import AbstractMethod
from AbstractClasses import AbstractNetworkComponent
from LoggingConfig import logger
import ThreadShares as TS


#################################
# Root Methods 


class ResponderAnalyzeInterface(AbstractMethod):
	_name = "responder analyze interface"
	_filename = "outputs/responderAI.out"

	def __init__self():
		pass

	@staticmethod
	def to_str() -> str:
		name = ResponderAnalyzeInterface._name
		return f"{name}"

	@staticmethod
	def run(commands_q:queue.Queue, interface:AbstractNetworkComponent) -> None:
		method_name = ResponderAnalyzeInterface._name
		output_file = ResponderAnalyzeInterface._filename

		cmd = f"sudo responder -AI {interface.interface_name}"
		
		# create the event and send it to the event-thread
		new_event = Run_Event(type='run', command=cmd, method=ResponderAnalyzeInterface, nc=interface)
		commands_q.put(new_event)
		return

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True



class PortScan(AbstractMethod):
	_name = 'port scan'
	_filename = 'outputs/port_scan'

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{PortScan._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent) -> list:
		"""
		nc should be a Network (component) for us to be able
		to get the network address.
		"""
		# obter o ip do host
		_ip = nc.get_ip()
		if _ip == None:
			return []

		# obter o output file com o ip do host
		str_ip = str(_ip).replace('.','_')
		output_file = PortScan._filename +str_ip + '.out'
		# chamar o comando para listar os portos
		cmd = f"sudo nmap -sS -n -Pn {_ip}"
		# criar o evento de run com o comando
		return [Run_Event(type='run', filename=output_file, command=cmd, method=PortScan, nc=nc)]

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True


class CheckIfSMBServiceIsRunning(AbstractMethod):
	_name = 'check if SMB service is running'
	_filename = 'outputs/nmap_port_445'
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{CheckIfSMBServiceIsRunning._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict) -> list:
		"""
		defines the command events for this class.
		"""
		# check for the context variables
		if context is None:
			logger.warning("No context for CheckIfSMBServiceIsRunning")
			return []

		# check for the specific requirements in context
		if not CheckIfSMBServiceIsRunning.check_context(context):
			return []

		# must be locked accessing shared memory
		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if CheckIfSMBServiceIsRunning.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			CheckIfSMBServiceIsRunning._previous_args.add(args)

		# get the output file name
		str_ip = str(ip).replace('.','_')
		output_file = CheckIfSMBServiceIsRunning._filename +str_ip + '.out'
		# construct the command
		cmd = f"sudo nmap -p 139,445 -n -Pn {ip}"

		# create the event 
		return [Run_Event(type='run', filename=output_file, command=cmd, method=CheckIfSMBServiceIsRunning, nc=nc, context=context)]

	def get_context(nc:AbstractNetworkComponent):
		"""
		Nothing for now
		"""
		pass

	@staticmethod 
	def check_if_args_were_already_used(arg: tuple):
		"""
		checks if the args were already used, if so don't create the run events. 
		MUST BE USED WITH A LOCK
		"""
		if arg in CheckIfSMBServiceIsRunning._previous_args: # O(1) average
			logger.debug(f"arg for CheckIfSMBServiceIsRunning was already used ({arg})")
			return True
		return False

	@staticmethod
	def check_context(context:dict):
		"""
		checks for requirements, if we have all the information we need in the context
		"""
		if context['ip'] is None: 
			logger.debug(f"context for CheckIfSMBServiceIsRunning doesn't have an ip")
			return False
		if context['network_address'] is None:
			logger.debug(f"context for CheckIfSMBServiceIsRunning doesn't have a network address")
			return False
		if context['interface_name'] is None:
			logger.debug(f"context for CheckIfSMBServiceIsRunning doesn't have an interface name")
			return False
		return True

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True




class CheckIfMSRPCServiceIsRunning(AbstractMethod):
	_name = 'check if MSRPC service is running'
	_filename = 'outputs/nmap_port_135'
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{CheckIfMSRPCServiceIsRunning._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict) -> list:
		"""
		Will need the ip, the network and interface name
		"""
		if context is None:
			logger.debug(f"CheckIfMSRPCServiceIsRunning didn't received a context from ({nc})")
			return []
		
		if not CheckIfMSRPCServiceIsRunning.check_context(context):
			return []

		# must be locked accessing shared memory:
		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
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
		return [Run_Event(type='run', filename=output_file, command=cmd, method=CheckIfMSRPCServiceIsRunning, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
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




class NBNSGroupMembers(AbstractMethod):
	_name = 'find the members of netbios group'
	_filename = "outputs/nmblookup-"
	_previous_args = set()
	
	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{NBNSGroupMembers._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict) -> list:
		"""
		Creates the run events for this method using a network component.
		NC should be a NetBIOSGroup in most cases
		"""		
		# context couldn't extract necessary fields
		if len(context) == 0:
			logger.debug(f"NBNSGroupMembers didn't receive any context from ({nc})")
			return []

		# check if the context has the required values
		if not NBNSGroupMembers.check_context(context):
			return []

		# must be locked accessing shared memory
		with TS.shared_lock:
			# extract the specific context for this command
			group_id = context['group_id']
			list_args = list(group_id)
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

		return [Run_Event(type='run', filename=output_file, command=cmd, method=NBNSGroupMembers, nc=nc, context=context)]


	@staticmethod
	def check_for_objective(nc):
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



class NBNSIPTranslation(AbstractMethod):
	_name = "ip to hostname through NBNS"
	_filename = "outputs/nmblookup-A-"
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{NBNSIPTranslation._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a livehost. 
		"""
		if context is None:
			# get context
			logger.debug(f"NBNSIPTranslation didn't receive a context from ({nc})")
			return []

		# if it doesn't have the necessary context values
		if not NBNSIPTranslation.check_context(context):
			return []

		with TS.shared_lock:
			ip = context['ip']
			list_args = list(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if NBNSIPTranslation.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			NBNSIPTranslation._previous_args.add(args)

		context_ip_address = context['ip']
		str_ip_address = context_ip_address.replace('.', '_')
		# output file
		output_file = NBNSIPTranslation._filename +str_ip_address +'.out'

		cmd =  f"nmblookup -A {context_ip_address}"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=NBNSIPTranslation, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True


	@staticmethod
	def check_if_args_were_already_used(args:tuple):
		"""
		checks if the args were already used, if so don't create 
		the run events
		MUST be used with a lock.
		"""
		if arg in NBNSIPTranslation._previous_args:
			logger.debug(f"arg for NBNSIPTranslation was already used ({arg})")
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
			logger.debug(f"context for NBNSIPTranslation doesn't have an ip")
			return False
		return True



class DumpInterfaceEndpointsFromEndpointMapper(AbstractMethod):
	_name = 'dump interface endpoints from endpoint mapper'
	_filename = 'outputs/rpcdump-'
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod 
	def to_str():
		return f"{DumpInterfaceEndpointsFromEndpointMapper._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a rpc server
		"""
		if context is None:
			logger.debug(f"DumpInterfaceEndpointsFromEndpointMapper didn't receive a context from ({nc})")
			return []

		if not DumpInterfaceEndpointsFromEndpointMapper.check_context(context):
			return []

		# must be locked accessing shared memory
		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if DumpInterfaceEndpointsFromEndpointMapper.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			DumpInterfaceEndpointsFromEndpointMapper._previous_args.add(args)


		# command to run 
		cmd = f"rpcdump.py {ip}"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = DumpInterfaceEndpointsFromEndpointMapper._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=DumpInterfaceEndpointsFromEndpointMapper, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
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
		if context['ip'] is None :
			logger.debug(f"context for DumpInterfaceEndpointsFromEndpointMapper doesn't have an ip")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in DumpInterfaceEndpointsFromEndpointMapper._previous_args:
			logger.debug(f"arg for DumpInterfaceEndpointsFromEndpointMapper was already used ({arg})")
			return True 
		return False 





class EnumDomainTrustsThroughRPC(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'enum domains trusts through rpc'
	_filename = 'outputs/rpc-dsenumdomtrusts-'
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainTrustsThroughRPC._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a MSRPC server
		"""
		if context is None:
			return []
		
		if not EnumDomainTrustsThroughRPC.check_context(context):
			return []

		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if EnumDomainTrustsThroughRPC.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			EnumDomainTrustsThroughRPC._previous_args.add(args)

		# command to run 
		#cmd = f"rpcclient -U=\"foxriver.local/DrTancredi%Password123\" {ip} -c=\'dsenumdomtrusts\'"
		cmd = f"rpcclient {ip} -c=\'dsenumdomtrusts\' -U=\'%\'"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = EnumDomainTrustsThroughRPC._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=EnumDomainTrustsThroughRPC, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True

	@staticmethod
	def check_context(context:dict):
		"""
		Checks if the context has the spefici required values
		to be run, if it doesn't don't create the run events
		"""
		if context['domain_name'] is None:
			logger.debug(f"context for EnumDomainTrustsThroughRPC doesn't have a domain_name")
			return False 
		if context['ip'] is None:
			logger.debug(f"context for EnumDomainTrustsThroughRPC doesn't have an ip")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainTrustsThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainTrustsThroughRPC was already used ({arg})")
			return True 
		return False 





class EnumDomainsThroughRPC(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'enumdomains through rpc'
	_filename = 'outputs/rpc-enumdomains-'
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainsThroughRPC._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a MSRPC server
		"""
		if context is None:
			logger.debug(f"EnumDomainsThroughRPC didn't receive a context from ({nc})")
			return []

		if not EnumDomainsThroughRP.check_context(context):
			return []

		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if EnumDomainsThroughRPC.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			EnumDomainsThroughRPC._previous_args.add(args)

		# command to run 
		#cmd = f"rpcclient -U=\"foxriver.local/DrTancredi%Password123\" {context_ip_address} -c=\'enumdomains\'"
		cmd = f"rpcclient {ip} -c=\'enumdomains\' -U=\'%\'"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = EnumDomainsThroughRPC._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=EnumDomainsThroughRPC, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
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
		if context['ip'] is None :
			logger.debug(f"context for EnumDomainsThroughRPC doesn't have an associated_object")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainsThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainsThroughRPC was already used ({arg})")
			return True 
		return False 



class EnumDomainUsersThroughRPC(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'enum domain users through rpc'
	_filename = 'outputs/rpc-enumdomusers-'
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainUsersThroughRPC._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a MSRPC server
		"""
		if context is None:
			logger.debug(f"EnumDomainUsersThroughRPC didn't receive a context from ({nc})")
			return []

		if not EnumDomainUsersThroughRPC.check_context(context):
			return []

		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if EnumDomainUsersThroughRPC.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			EnumDomainUsersThroughRPC._previous_args.add(args)

		# if we still don't have the domain for this rpc
		if context['domain_name'] is None:
			logger.debug(f"couldn't construct event for method EnumDomainUsersThroughRPC, there was no domain name")
			return []

		# command to run 
		#cmd = f"rpcclient -U=\"foxriver.local/DrTancredi%Password123\" {context_ip_address} -c=\'enumdomusers\'"
		cmd = f"rpcclient {ip} -c=\'enumdomusers\' -U=\'%\'"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = EnumDomainUsersThroughRPC._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=EnumDomainUsersThroughRPC, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
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
		if context['ip'] is None :
			logger.debug(f"context for EnumDomainUsersThroughRPC doesn't have an ip")
			return False
		# if we don't have a group id for the object
		if context['domain_name'] is None:
			logger.debug(f"context for EnumDomainUsersThroughRPC doesn't have a domain_name")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainUsersThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainUsersThroughRPC was already used ({arg})")
			return True 
		return False 


class EnumDomainGroupsThroughRPC(AbstractMethod):
	"""
	IT HAS CREDENTIALS: CHANGE THIS
	"""
	_name = 'enum domain groups through rpc'
	_filename = 'outputs/rpc-enumdomgroups-'
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{EnumDomainGroupsThroughRPC._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a MSRPC server
		"""
		if context is None:
			logger.debug(f"EnumDomainGroupsThroughRPC didn't receive a context from ({nc})")
			return []

		if not EnumDomainGroupsThroughRPC.check_context(context):
			return []

		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if EnumDomainGroupsThroughRPC.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			EnumDomainGroupsThroughRPC._previous_args.add(args)

		#cmd = f"rpcclient -U=\"foxriver.local/DrTancredi%Password123\" {context_ip_address} -c=\'enumdomgroups\'"
		cmd = f"rpcclient {ip} -c=\'enumdomgroups\' -U=\'%\'"

		# output file 
		str_ip_address = ip.replace('.', '_')
		output_file = EnumDomainGroupsThroughRPC._filename + str_ip_address + '.out'
		return [Run_Event(type='run', filename=output_file, command=cmd, method=EnumDomainGroupsThroughRPC, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
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
		if context['ip'] is None :
			logger.debug(f"context for EnumDomainGroupsThroughRPC doesn't have an ip")
			return False
		# if we don't have a group id for the object
		if context['domain_name'] is None:
			logger.debug(f"context for EnumDomainGroupsThroughRPC doesn't have a domain_name")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in EnumDomainGroupsThroughRPC._previous_args:
			logger.debug(f"arg for EnumDomainGroupsThroughRPC was already used ({arg})")
			return True 
		return False



class QueryRootDSEOfDCThroughLDAP(AbstractMethod):
	_name = "query root dse of DC through LDAP"
	_filename = "outputs/nmap-script-rootdse-LDAP"
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{QueryRootDSEOfDCThroughLDAP._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a livehost. 
		"""
		logger.debug(f"creating run events for method: {QueryRootDSEOfDCThroughLDAP._name} for nc: ({nc})")

		if context is None:
			logger.debug(f"QueryRootDSEOfDCThroughLDAP didn't receive any context from ({nc})")
			return []

		if not QueryRootDSEOfDCThroughLDAP.check_context(context):
			return []

		with TS.shared_lock:
			# extract the specific context for this command
			ip = context['ip']
			list_args = list(ip)
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
		return [Run_Event(type='run', filename=output_file, command=cmd, method=QueryRootDSEOfDCThroughLDAP, nc=nc, context=context)]

	@staticmethod
	def get_context(nc:AbstractNetworkComponent):
		return nc.get_context()

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		with TS.shared_lock:
			nc.get_context()
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
		# if we don't have a group id for the object
		if context['domain_name'] is None:
			logger.debug(f"context for QueryRootDSEOfDCThroughLDAP doesn't have a domain_name")
			return False
		return True




class ArpScan(AbstractMethod):
	_name = "arp scan"
	_filename = "outputs/arpscan"
	_previous_args = set()

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{ArpScan.name}"


	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a Network (component) for us to be able
		to get the network address.
		"""

		if context is None:
			logger.debug(f"ArpScan didn't receive any context from ({nc})")
			return []

		if not ArpScan.check_context(context):
			return []

		with TS.shared_lock:
			# extract the specific context for this command
			network_address = context['network_address']
			list_args = list(network_address)
			# check if this method was already called with these arguments
			args = tuple(list_args) # the tuple of args used 
			if ArpScan.check_if_args_were_already_used(args):
				return []
			# add this argument to the set of arguments that were already used
			ArpScan._previous_args.add(args)

		str_network_address = str(network_address).replace('/','_')
		str_network_address = str_network_address.replace('.', '_')
		# output file
		output_file = ArpScan._filename +str_network_address +'.out'

		cmd =  f"sudo nmap -PR -sn -n {network_address}"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=ArpScan, nc=nc, context=context)]

	@staticmethod
	def check_for_objective(nc):
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
		if arg in ArpScan._previous_args:
			logger.debug(f"arg for ArpScan was already used ({arg})")
			return True 
		return False 

	@staticmethod
	def check_context(context:dict):
		"""
		Checks if the context provided to run the method has the
		necessary values
		"""
		# it is not associated with an object
		if context['our_ip'] is None :
			logger.debug(f"context for ArpScan doesn't have our_ip")
			return False
		# if we don't have a group id for the object
		if context['network_address'] is None:
			logger.debug(f"context for ArpScan doesn't have a network_address")
			return False
		return True





class ListInterfaces(AbstractMethod):
	_name = "list interfaces"
	_filename = "outputs/ListInterfaces.out"

	# doesn't need anything to run 
	def __init__(self):
		pass

	@staticmethod
	def to_str() -> str: 
		name = OurIPs_Executioner._name
		return f"{name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict) -> list:
		method_name = ListInterfaces._name
		output_file = ListInterfaces._filename

		# context can be empty dict, but not None
		if context is None:
			logger.debug(f"ListInterfaces didn't receive any context from ({nc})")
			return []

		cmd = "ip a"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=ListInterfaces, nc=nc, context=context)]

	@staticmethod
	def get_context(nc:AbstractNetworkComponent):
		# get the root object
		root_obj = nc.get_root()
		if root_obj is None:
			return dict()
		context = {'root': root_obj}
		return context

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True