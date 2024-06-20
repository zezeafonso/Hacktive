import queue

from Events import Run_Event
from AbstractClasses import AbstractMethod
from AbstractClasses import AbstractNetworkComponent


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


class CheckIfSMBServiceIsRunning(AbstractMethod):
	_name = 'check if SMB service is running'
	_filename = 'outputs/nmap_port_445'

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
			context = CheckIfSMBServiceIsRunning.get_context(nc)
			if context is None:
				logger.warning("No context for CheckIfSMBServiceIsRunning")
				return []

		# check for the specific requirements
		if 'ip' not in context or 'network_address' not in context or 'interface_name' not in context:
			return []

		# extract the specific context for this command
		ip = context['ip']
		network_address = context['network_address']
		interface_name = context['interface_name'] 

		# obter o output file com o ip do host
		str_ip = str(ip).replace('.','_')
		output_file = CheckIfSMBServiceIsRunning._filename +str_ip + '.out'
		# chamar o comando para listar os portos
		cmd = f"sudo nmap -p 139,445 -n -Pn {ip}"
		# criar o evento de run com o comando
		return [Run_Event(type='run', filename=output_file, command=cmd, method=CheckIfSMBServiceIsRunning, nc=nc, context=context)]

	def get_context(nc:AbstractNetworkComponent):
		"""
		Nothing for now
		"""
		pass



class CheckIfMSRPCServiceIsRunning(AbstractMethod):
	_name = 'check if MSRPC service is running'
	_filename = 'outputs/nmap_port_135'

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
			CheckIfMSRPCServiceIsRunning.get_context(nc) # nothing for now 
		
		if context['ip'] is None or context['network_address'] is None or context['interface_name'] is None:
			return [] # nothing to do in this case

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


	def get_context(nc:AbstractNetworkComponent):
		"""
		nothing for now 
		"""
		pass




class NBNSGroupMembers(AbstractMethod):
	_name = 'find the members of netbios group'
	_filename = "outputs/nmblookup-"
	
	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{NBNSGroupMembers._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent) -> list:
		"""
		Creates the run events for this method using a network component.
		NC should be a NetBIOSGroup in most cases
		"""	
		context = NBNSGroupMembers.get_context(nc)
		
		# context couldn't extract necessary fields
		if len(context) == 0:
			return []

		group_id = context['group_id']
		# output file
		output_file = NBNSGroupMembers._filename + group_id +'.out'

		cmd =  f"nmblookup '{group_id}'"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=NBNSGroupMembers, nc=nc, context=context)]



	def get_context(nc:AbstractNetworkComponent):
		"""
		Supposes that the nc is a NetBIOSGroup object
		"""
		# get the object to which is associated 
		network_name = nc.associated.network_address
		interface_name = nc.associated.get_interface().interface_name
		group_id = nc.id

		if network_name is None or interface_name is None or group_id is None:
			return {}

		context = {'group_id': group_id, 'network':network_name, 'interface':interface_name}
		return context



class NBNSIPTranslation(AbstractMethod):
	_name = "ip to hostname through NBNS"
	_filename = "outputs/nmblookup-A-"

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
			context = NBNSIPTranslation.get_context(nc)
			if len(context) == 0:
				return []

		context_ip_address = context['ip']
		str_ip_address = context_ip_address.replace('.', '_')
		# output file
		output_file = NBNSIPTranslation._filename +str_ip_address +'.out'

		cmd =  f"nmblookup -A {context_ip_address}"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=NBNSIPTranslation, nc=nc, context=context)]

	@staticmethod
	def get_context(nc:AbstractNetworkComponent):
		# get the host object (if it wasn't a host sending this)
		host_with_ip = nc.get_host().ip
	
		network_name = nc.get_network().network_address
		interface_name = nc.get_interface().interface_name
		if host_with_ip is None or network_name is None:
			return dict()
		context = {'ip':host_with_ip, 'network':network_name, 'interface':interface_name}
		return context



class QueryNamingContextOfDCThroughLDAP(AbstractMethod):
	_name = "query naming context of DC through LDAP"
	_filename = "outputs/naming-context-LDAP"

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{QueryNamingContextOfDCThroughLDAP._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent, context:dict=None) -> list:
		"""
		nc should be a livehost. 
		"""
		if context is None:
			# get context through the function
			context = QueryNamingContextOfDCThroughLDAP.get_context(nc)
			if len(context) == 0:
				return []

		context_ip_address = context['ip']
		str_ip_address = context_ip_address.replace('.', '_')
		# output file
		output_file = QueryNamingContextOfDCThroughLDAP._filename+'-'+str_ip_address +'.out'

		cmd =  f"ldapsearch -H ldap://{context_ip_address} -x -s base namingcontexts"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=QueryNamingContextOfDCThroughLDAP, nc=nc, context=context)]

	@staticmethod
	def get_context(nc:AbstractNetworkComponent):
		# get the host object (if it wasn't a host sending this)
		host_with_ip = nc.get_host().ip
		network_name = nc.get_network().network_address
		interface_name = nc.get_interface().interface_name

		if host_with_ip is None or network_name is None or interface_name is None:
			print(f"can't obtain the context for the LDAP method")
			return dict()

		context = {'ip':host_with_ip, 'network':network_name, 'interface':interface_name}
		return context


class ArpScan(AbstractMethod):
	_name = "arp scan"
	_filename = "outputs/arpscan"

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
			# get context
			context = ArpScan.get_context(nc)
			if len(context) == 0:
				return []

		# get the str of the network addresss
		context_net_address = context['network']
		str_network_address = str(context_net_address).replace('/','_')
		str_network_address = str_network_address.replace('.', '_')
		# output file
		output_file = ArpScan._filename +str_network_address +'.out'

		cmd =  f"sudo nmap -PR -sn -n {context_net_address}"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=ArpScan, nc=nc, context=context)]

	def get_context(nc:AbstractNetworkComponent) -> dict:
		# get the network object
		network_name = nc.get_network_address()
		interface_name = nc.get_interface().get_interface_name()
		if network_name is None or interface_name is None:
			return dict()
		context = {'network':network_name, 'interface':interface_name}
		return context





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
	def create_run_events(nc:AbstractNetworkComponent) -> list:
		method_name = ListInterfaces._name
		output_file = ListInterfaces._filename

		# get context
		context = ListInterfaces.get_context(nc)
		if len(context) == 0:
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