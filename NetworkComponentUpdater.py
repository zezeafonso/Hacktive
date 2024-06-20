

import Methods
import ThreadShares as TS
import FilterObjects as FO
from AbstractClasses import AbstractMethod
from LoggingConfig import logger



def init_root_object(obj):
	global root_obj 
	root_obj = obj


"""
context must have root object
"""
def update_components_found_new_interface(context, filtered_obj:FO.Filtered_NewInterface):
	"""
	What we do when filter found a Filtered object
	of type filtered_newinterface

	returns dict 'object' and 'methods' (if a new
	interface network component was created)
	"""
	global root_obj

	# get interface name
	interface_name = filtered_obj.get_interface()

	# the auto methods to run after this
	methods = []

	# LOCK
	with TS.shared_lock:
		logger.debug(f"interface: ({interface_name}) found -> updating components")
		answer = root_obj.get_interface_or_create_it(interface_name)
		methods += answer['methods'] # just one method
		return methods




def update_components_found_new_network_for_interface(context, filtered_obj:FO.Filtered_NewNetworkForInterface):
	"""
	What we do when we receive a filtered_new_network_for_interface

	we get or create the interface.
	And for that interface we get or create the network.

	returns a dict with 'object' and 'methods' (if we created
	a new network or interface objects)
	"""
	global root_obj

	interface_name = filtered_obj.get_interface()
	network_name = filtered_obj.get_network()
	auto_functions = []

	# LOCK
	with TS.shared_lock:
		logger.debug(f"network ({network_name}) for interface ({interface_name}) found -> updating components")
		answer = root_obj.get_interface_or_create_it(interface_name)
		
		interface_obj = answer['object']
		auto_functions += answer['methods']
		
		# ASKS THE USER IF HE WANTS THIS NETWORK
		answer = interface_obj.get_network_or_create_it(network_name)
		auto_functions += answer['methods']

		return auto_functions





def update_components_found_our_ip_for_a_network(context, filtered_obj:FO.Filtered_FoundOurIPForNetwork):
	"""
	Defines what components we update when we find OUR
	IP for a particular network

	gets or creates the interface
	gets or creates the network for the interface
	updates the network component to have our ip 
	"""
	print(f"Found our ip in filter of list interfaces")
	global root_obj
	auto_functions = []

	# network and ip from filtered_obj
	interface_name = filtered_obj.get_interface()
	network_name = filtered_obj.get_network()
	ip = filtered_obj.get_ip()

	# LOCK
	with TS.shared_lock:
		answer = root_obj.get_interface_or_create_it(interface_name)
		interface_obj = answer['object']
		auto_functions += answer['methods']
		
		answer = interface_obj.get_network_or_create_it(network_name)
		network_obj = answer['object']
		auto_functions += answer['methods']

		network_obj.add_our_ip(ip)

		return auto_functions


def update_components_found_NetBIOS_hostname_for_ip(context, filtered_obj:FO.Filtered_FoundNetBIOSHostnameForIP):
	"""
	Defines the componets we update when we find a netbios
	hostname for a host with an IP.

	we get or create a Netbios_worstation role for that ip, 
	with the hostname we found.
	"""

	network_obj = context['network']

	hostname = filtered_obj.get_hostname()
	ip = filtered_obj.get_ip()

	with TS.shared_lock:
		methods = network_obj.associate_netbios_workstation_to_ip_host_through_hostname(hostname, ip)
		#methods = network_obj.attach_NetBIOS_hostname_to_ip_host(hostname, ip)
		return methods




def found_new_ip_for_network(context, filtered_obj:FO.Filtered_NewIPForNetwork):
	"""
	Defines the components we update when we find an IP 
	that is alive in a network

	we get or crerate the IP host.
	"""
	network_obj = context['network']
	ip = filtered_obj.get_ip()

	with TS.shared_lock:
		logger.debug(f"updating components found new ip ({ip}) for network ({network_obj.network_address})")
		answer = network_obj.get_ip_host_or_create_it(ip)
		return answer['methods'] # we don't need the object



def update_components_found_NetBIOS_hostname_hosting_smb(context, filtered_obj:FO.Filtered_FoundNetBIOSHostnameWithSMB):
	"""
	Defines the components we update when we find a 
	netbios hostname hosting an smb service
	"""
	network_obj = context['network']
	hostname = filtered_obj.get_hostname()

	auto_functions = []

	# if the hostname doesn't exist, create it.
	with TS.shared_lock:
		# retrieve or create the host object
		answer = network_obj.get_or_create_netbios_workstation_through_hostname(hostname=hostname)

		netbios_workstation_obj = answer['object']
		auto_functions += answer['methods'] # only if it's a new host

		# get or create the NetBIOS Smb Server for this
		answer = netbios_workstation_obj.get_netbios_smb_server_or_create_it()
		auto_functions += answer['methods']

	return auto_functions


def associate_existing_netbios_group_to_host_ip(context, filtered_obj:FO.Filtered_FoundNetBIOSGroupForIP):
	"""
	what we do when we found a netbios grup for an ip
	(important) the group object was already created before using the function

	we retrieve or create the netbios workstation role 
	for this host, and then we associate this group to it
	if not done already.
	"""
	network_obj = context['network']
	group_obj = context['group']
	ip_host = context['host']

	auto_functions = []

	# with lock update the information on the netbios group
	with TS.shared_lock:
		nw_obj = ip_host.get_netbios_workstation_obj()
		if nw_obj is None:
			ip_host.add_role_netbios_workstation(hostname=None)
			nw_obj = ip_host.get_netbios_workstation_obj()
		auto_functions += nw_obj.add_group(group_obj) # empty list of list with auto functions

	return auto_functions


def update_components_found_pdc_for_netbios_group(context, filtered_obj):
	"""
	Updates the network components when we find a pdc for a netbios group.
	+ We will get/create the netbios workstation for this host.
	+ get/create the netbios group associated to this netbios workstation
	+ update the roles for that group

	Doesn't launch any methods for now 
	"""
	network_obj = context['network']
	host_obj = context['host']

	netbios_group = filtered_obj.get_netbios_group()

	auto_functions = []

	with TS.shared_lock:
		nw_obj = host_obj.get_netbios_workstation_obj()
		if nw_obj is None:
			logger.debug(f"There was no network station obj for this ip ({host_obj.get_ip()})")
		# get or create the group from the netbios workstation
		group_obj = nw_obj.get_group_from_group_id(netbios_group.lower()+'#'+'00')
		if group_obj is None:
			logger.debug(f"there was no group_obj with group id: {group_id} in the netbios workstation ")
		# update the roles 
		auto_functions += nw_obj.add_pdc_role_for_group(group_obj)

	return auto_functions



def update_components_found_new_domain_components_path_ldap(context_for_updates, filtered_obj):
	"""
	Updates the network components for the event of finding new 
	domain components path through ldap. 
	We found a ldap server and we might have found a Domain Controller's domain name.

	+ we received a filtered object from the filter it means that the 
	service is on. Which means this host (if it doesn't have already) 
	must have an ldap service associated. 

	Next we must check if any of the names corresponds to a domain name
	"""
	host_obj = context_for_updates['host']
	domain_components_path = filtered_obj.get_dc_path()

	auto_functions = []

	with TS.shared_lock:
		# create or get the ldap server role for this host
		answer = host_obj.get_or_add_role_ldap_server()
		ldap_server = answer['object']
		auto_functions += answer['methods']

		# update it's domain name
		ldap_server.check_if_ldap_domain_components_path_is_domain_path(domain_components_path)

	return auto_functions
	


def found_netbios_group(context_for_updates, filtered_obj):
	"""
	The components we update when we find a netbios group.
	We will create the netbios (if doesn't exist) group object first, then 
	associate it with the correct network, the one used 
	when we called the command 

	returns a dictionary with the group object and the auto-methods 
	answer['object']
	answer['methods']

	TODO: check if we have a WINS server in the network, 
	this way you should associate the netbios group we find to 
	that object instead of the network.
	"""
	network_obj = context_for_updates['network']
	group_name = filtered_obj.get_netbios_group() 
	group_type = filtered_obj.get_type()
	
	auto_functions = []

	with TS.shared_lock:
		# if we haven't found this group yet
		if not network_obj.check_if_netbios_group_exists(group_name, group_type):
			# create the group network component
			answer = network_obj.create_netbios_group(group_name, group_type)

			# associate the netbios group to the network 
			network_obj.associate_netbios_group_to_this_network(answer['object'])

			# associate the netbios group with an object (network, or Wins server)
			netbios_group_obj = answer['object'] 
			netbios_group_obj.associate_with_object(network_obj)

			# get the auto methods for netbios group found 
			answer['methods'] += [netbios_group_obj.auto]
	return answer

		

def found_netbios_group_for_ip(context_for_updates, filtered_obj):
	"""
	Defines the components we update when we find a netbios group
	for an ip.
	The group may not yet exist in our objects. 
	The ip may also not exist
	"""
	auto_functions = list()
	
	# get the NetBIOSgroup object and the methods 
	answer = found_netbios_group(context_for_updates, filtered_obj)
	auto_functions += answer['methods']

	# update context for the next function
	context_for_next_func = context_for_updates
	context_for_next_func['group'] = answer['object'] # the group object we created

	# retrieve the host object from ip 
	network_obj = context_for_updates['network']
	ip = filtered_obj.get_ip()
	answer = network_obj.get_ip_host_or_create_it(ip)
	if answer['methods'] != []: # just for precaution
		auto_functions += answer['methods']
	ip_host = answer['object']

	# update context for next function 
	context_for_next_func['host'] = ip_host

	auto_functions += associate_existing_netbios_group_to_host_ip(context_for_next_func, filtered_obj)
	return auto_functions


def found_pdc_for_netbios_group(context, filtered_obj):
	network_obj = context['network']
	ip = filtered_obj.get_ip()

	auto_functions = []

	with TS.shared_lock:
		answer = network_obj.get_ip_host_or_create_it(ip)
		if answer['methods'] != []:
			auto_functions += answer['methods']
		ip_host = answer['object']

	context_for_function = context
	context_for_function['host'] = ip_host

	with TS.shared_lock:
		auto_functions += update_components_found_pdc_for_netbios_group(context_for_function, filtered_obj)

	return auto_functions


def found_netbios_hostname_with_smb_active(context, filtered_obj):
	"""
	What we do when we find a netbios hostsname with active SMB 
	DC1             <20> -         B <ACTIVE> 

	the hostname was already sent as a filtered obj, and so is created 
	for the host ip, that launched this command.
	"""
	network_obj = context['network']
	ip = filtered_obj.get_ip()

	auto_functions = []

	with TS.shared_lock:
		# retrieve the host object
		answer = network_obj.get_ip_host_or_create_it(ip)
		if answer['methods'] != []: # as precaution
			auto_functions += answer['methods']
		ip_host = answer['object']

		nw_obj = ip_host.get_netbios_workstation_obj()
		if nw_obj is None:
			print(f"No Netbios workstation for this host {ip}")
		auto_functions += nw_obj.add_netbios_smb_server()
		print(f"IP: {ip}")

	return auto_functions




"""
Update functions by method
"""


def update_list_interfaces(context:dict, filtered_objects:list):
	"""
	Defines the components we update when we list the interfaces available
	"""
	# for this update the context will just be the root object
	if context['root'] is None:
		return 

	auto_functions = list()

	# context is only the root object
	root_obj = context['root']

	for filtered_obj in filtered_objects:
		# FOUND NEW INTERFACE
		if isinstance(filtered_obj, FO.Filtered_NewInterface):
			methods = update_components_found_new_interface(context, filtered_obj)
			auto_functions += methods

		# FOUND NEW NETWORK FOR AN INTERFACE
		elif isinstance(filtered_obj, FO.Filtered_NewNetworkForInterface):
			methods = update_components_found_new_network_for_interface(context, filtered_obj)
			auto_functions += methods

		# FOUND OUR IP
		elif isinstance(filtered_obj, FO.Filtered_FoundOurIPForNetwork):
			methods = update_components_found_our_ip_for_a_network(context, filtered_obj)
			auto_functions += methods

	# return the list of objects that are new
	return auto_functions




def update_ip_to_host_nbns(context, filtered_objects):
	global root_obj
	# for this update the context will just be the root object
	if context['network'] is None or context['interface'] is None:
		return 

	auto_functions = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network']
	int_name = context['interface']

	# retrieve interface and network objects (both methods have locks)
	answer = root_obj.get_interface_or_create_it(int_name)
	int_obj = answer['object']
	answer = int_obj.get_network_or_create_it(net_name)
	net_obj = answer['object']

	context_for_updates = {'network':net_obj}

	auto_functions = list() # the list of new objects created

	for filtered_obj in filtered_objects:
		# FOUND HOSTNAME FOR IP
		if isinstance(filtered_obj, FO.Filtered_FoundNetBIOSHostnameForIP):
			logger.debug(f"filter found a hostname {filtered_obj.get_hostname()} for ip {filtered_obj.get_ip()}")
			auto_functions += update_components_found_NetBIOS_hostname_for_ip(context_for_updates, filtered_obj)

		# FOUND HOSTNAME WITH SMB ACTIVE - TODO 
		# this hostname might not yet exist in the network 
		if isinstance(filtered_obj, FO.Filtered_FoundNetBIOSHostnameWithSMB):
			logger.debug(f"filter foudn a hostname {filtered_obj.get_hostname()} using SMB")
			auto_functions += found_netbios_hostname_with_smb_active(context_for_updates, filtered_obj)
		
		# FOUND NETBIOS GROUP FOR IP 
		if isinstance(filtered_obj, FO.Filtered_FoundNetBIOSGroupForIP):
			logger.debug(f"filter found a group {filtered_obj.get_netbios_group()} for ip {filtered_obj.get_ip()}")
			auto_functions += found_netbios_group_for_ip(context_for_updates, filtered_obj)

		if isinstance(filtered_obj, FO.Filtered_FoundPDCIPForNetBIOSGroup):
			logger.debug(f"filter the ip {filtered_obj.get_ip()} is a PDC for {filtered_obj.get_netbios_group()}")
			auto_functions += found_pdc_for_netbios_group(context_for_updates, filtered_obj)
	
	return auto_functions




def update_arp_scan(context, filtered_objects):
	global root_obj

	# for this update the context will just be the root object
	if context['network'] is None or context['interface'] is None:
		return 

	auto_functions = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network']
	int_name = context['interface']

	# retrieve interface and network objects (both methods have locks)
	answer = root_obj.get_interface_or_create_it(int_name)
	int_obj = answer['object']
	answer = int_obj.get_network_or_create_it(net_name)
	net_obj = answer['object']

	context_for_updates = {'network':net_obj}

	for filtered_obj in filtered_objects:
		# FOUND NEW IP
		if isinstance(filtered_obj, FO.Filtered_NewIPForNetwork):
			logger.debug(f"Found new IP ({filtered_obj.get_ip()}) for network ({net_obj.network_address})")
			auto_functions += found_new_ip_for_network(context_for_updates, filtered_obj)

	return auto_functions


def update_query_naming_context_of_dc_through_ldap(context, filtered_objects):
	"""
	updates the components when we find a naminc context through 
	ldap 

	TODO: 
	+ implemenent locks
	+ implement the proper functioning when the objects don't exist
	"""
	global root_obj

	# for this update the context will just be the root object
	if context['network'] is None or context['interface'] is None or context['ip'] is None:
		return 

	auto_functions = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network']
	int_name = context['interface']
	host_name = context['ip']

	# retrieve interface and network objects (both methods have locks)
	answer = root_obj.get_interface_or_create_it(int_name)
	int_obj = answer['object']
	answer = int_obj.get_network_or_create_it(net_name)
	net_obj = answer['object']
	answer = net_obj.get_ip_host_or_create_it(context['ip'])
	host_obj = answer['object']

	context_for_updates = {'host': host_obj}

	for filtered_obj in filtered_objects:
		# FOUND A DOMAIN COMPONENTS PATH
		if isinstance(filtered_obj, FO.Filtered_DomainComponentsFromLDAPQuery):
			logger.debug(f"filter for ldap query to ip ({host_obj.ip}) found new domain components path {filtered_obj.get_dc_path()}")
			auto_functions += update_components_found_new_domain_components_path_ldap(context_for_updates, filtered_obj)

	return auto_functions


def update_check_if_smb_service_is_running(context:dict, filtered_objects:list):
	"""
	Defines the components we update when we find that a host
	is running a SMB service

	get the interface; get network; get host
	if host doesn't have already information that is running SMB
		add it.
	"""
	global root_obj

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None or context['ip'] is None:
		return 

	auto_functions = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_ip = context['ip']

	answer = root_obj.get_interface_or_create_it(int_name)
	int_obj = answer['object']
	answer = int_obj.get_network_or_create_it(net_name)
	net_obj = answer['object']
	answer = net_obj.get_ip_host_or_create_it(host_ip)
	host_obj = answer['object']

	for filtered_obj in filtered_objects:
		# FOUND A DOMAIN COMPONENTS PATH
		if isinstance(filtered_obj, FO.Filtered_SMBServiceIsUp):
			logger.debug(f"filter for checking if smb service is up for ip ({host_obj.ip}) found that it IS UP")
			answer = host_obj.found_smb_service_running_on_port(port=filtered_obj.get_port())
			auto_functions += answer['methods']



def update_check_if_msrpc_service_is_running(context:dict, filtered_objects:list):
	"""
	Defines the components we update when we find that a host
	is running a SMB service

	get the interface; get network; get host
	if host doesn't have already information that is running SMB
		add it.
	"""
	global root_obj

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None or context['ip'] is None:
		return 

	auto_functions = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_ip = context['ip']

	answer = root_obj.get_interface_or_create_it(int_name)
	int_obj = answer['object']
	answer = int_obj.get_network_or_create_it(net_name)
	net_obj = answer['object']
	answer = net_obj.get_ip_host_or_create_it(host_ip)
	host_obj = answer['object']

	for filtered_obj in filtered_objects:
		# FOUND A DOMAIN COMPONENTS PATH
		if isinstance(filtered_obj, FO.Filtered_MSRPCServiceIsUp):
			logger.debug(f"filter for checking if msrpc service is up for ip ({host_obj.ip}) found that it IS UP")
			answer = host_obj.found_msrpc_service_running_on_port(port=filtered_obj.get_port())
			auto_functions += answer['methods']

"""
Update network components (general function)
"""


def update_network_components(method:AbstractMethod, context:dict, filtered_objects:list):
	if method._name == 'list interfaces':
		return update_list_interfaces(context, filtered_objects)
	elif method._name == 'arp scan':
		return update_arp_scan(context, filtered_objects)
	elif method._name == 'ip to hostname through NBNS':
		return update_ip_to_host_nbns(context, filtered_objects)
	elif method._name == 'query naming context of DC through LDAP':
		return update_query_naming_context_of_dc_through_ldap(context, filtered_objects)
	elif method._name == 'check if SMB service is running':
		return update_check_if_smb_service_is_running(context, filtered_objects)
	elif method._name == 'check if MSRPC service is running':
		return update_check_if_msrpc_service_is_running(context, filtered_objects)

