

import Methods
import ThreadShares as TS
import FilterObjects as FO
from AbstractClasses import AbstractMethod



def init_root_object(obj):
	global root_obj 
	root_obj = obj

"""
if interface with this name exists just returns that object
if it doesn't, it will create the object and also return the auto methods
"""
def check_exists_retrieve_interface_or_interface_and_auto_methods(interface_name):
	global root_obj
	
	# if interface doesn't exist create it and get methods
	with TS.shared_lock:
		answer = root_obj.check_for_interface_name(interface_name)
		if answer['exists'] == 'no': # doesn't exist
			# create the interface, and get the auto methods
			answer = root_obj.create_interface_with_name(interface_name)
			interface_obj = answer['object']
			if answer['methods'] is not None:
				res = {'object':interface_obj, 'methods':answer['methods']}
			else:
				res = {'object':interface_obj, 'methods':[]}
		else:
			interface_obj = answer['object']
			res = {'object':interface_obj, 'methods':[]}
		return res



"""
if network with this name exists just returns that object
if it doesn't, it will create the object and also return the auto methods
"""
def check_exists_retrieve_network_or_network_and_auto_methods(interface_obj, network_str):
	# if network doesn't exist create it and get methods
	with TS.shared_lock:
		answer = interface_obj.check_for_network_str(network_str)
		if answer['exists'] == 'no': # doesn't exist
			# create the interface, and get the auto methods
			answer = interface_obj.create_network_with_network_str(network_str)
			network_obj = answer['object']
			if answer['methods'] != []:
				res = {'object':network_obj, 'methods':answer['methods']}
			else:
				res = {'object':network_obj, 'methods':[]}
		else:
			network_obj = answer['object']
			res = {'object':network_obj, 'methods':[]}
		return res


"""
if hosts with this ip exists just returns that object
if it doesn't, it will create teh object and also return the auto methods
"""
def check_ip_exists_retrieve_host_or_host_and_auto_methods(network_obj, ip):
	# if host doesn't exist create it and get methods
	answer = network_obj.check_for_host_with_ip(ip)
	if answer['exists'] == 'no':
		# if it's 'our ip' in the network
		if network_obj.our_ip == ip:
			print("found an equal to our ip")
			res = {'object':None, 'methods':[]}
			return res

		answer = network_obj.create_host_with_ip(ip)
		host_obj = answer['object']
		if answer['methods'] != []:
			res = {'object':host_obj, 'methods':answer['methods']}
		else:
			res = {'object':host_obj, 'methods':[]}
	# the host already existed, no methods found
	else:
		host_obj = answer['object']
		res = {'object': host_obj, 'methods': []}
	return res






"""
structure of the file:

------
update functions by method

-------
update general function
- the one that calls each independent updater
"""


"""
Update functions by filtered object
"""

"""
context must have root object
"""
def update_components_found_new_interface(context, filtered_obj:FO.Filtered_NewInterface):
	print(f"Found interface in filter of list interfaces")
	global root_obj

	# get interface name
	interface_name = filtered_obj.get_interface()
	# the auto methods to run after this
	methods = []

	# LOCK
	with TS.shared_lock:
		answer = check_exists_retrieve_interface_or_interface_and_auto_methods(interface_name)
		methods += answer['methods'] # just one method
		return methods

"""
context must have root object
"""
def update_components_found_new_network_for_interface(context, filtered_obj:FO.Filtered_NewNetworkForInterface):
	print(f"Found network in filter of list interfaces")
	global root_obj

	interface_name = filtered_obj.get_interface()
	network_name = filtered_obj.get_network()
	auto_methods = []

	# LOCK
	with TS.shared_lock:
		answer = check_exists_retrieve_interface_or_interface_and_auto_methods(interface_name)
		interface_obj = answer['object']
		auto_methods += answer['methods']
		
		answer = check_exists_retrieve_network_or_network_and_auto_methods(interface_obj, network_name)
		auto_methods += answer['methods']

		return auto_methods

"""
context must have interface object
"""
def update_components_found_our_ip_for_a_network(context, filtered_obj:FO.Filtered_FoundOurIPForNetwork):
	print(f"Found our ip in filter of list interfaces")
	global root_obj
	auto_methods = []

	# network and ip from filtered_obj
	interface_name = filtered_obj.get_interface()
	network_name = filtered_obj.get_network()
	ip = filtered_obj.get_ip()

	# LOCK
	with TS.shared_lock:
		answer = check_exists_retrieve_interface_or_interface_and_auto_methods(interface_name)
		interface_obj = answer['object']
		auto_methods += answer['methods']
		
		answer = check_exists_retrieve_network_or_network_and_auto_methods(interface_obj, network_name)
		network_obj = answer['object']
		auto_methods += answer['methods']

		network_obj.add_our_ip(ip)

		return auto_methods


def update_components_found_NetBIOS_hostname_for_ip(context, filtered_obj:FO.Filtered_FoundNetBIOSHostnameForIP):
	# network obj passed in context
	network_obj = context['network']
	# hostname and ip passed in filtered object
	hostname = filtered_obj.get_hostname()
	ip = filtered_obj.get_ip()

	with TS.shared_lock:
		methods = network_obj.attach_NetBIOS_hostname_to_ip_host(hostname, ip)
		return methods


def update_components_found_new_ip_for_network(context, filtered_obj:FO.Filtered_NewIPForNetwork):
	network_obj = context['network']
	ip = filtered_obj.get_ip()

	print(f"i found a new ip {ip}")
	print(f"our ip: {network_obj.our_ip}")

	with TS.shared_lock:
		answer = check_ip_exists_retrieve_host_or_host_and_auto_methods(network_obj, ip)
		if answer['object'] is not None:
			print(f"object: {answer['object']} with ip: {answer['object'].ip}")
		print(f"answer methods: {answer['methods']}")
		return answer['methods'] # we don't need the object



def update_components_found_NetBIOS_hostname_hosting_smb(context, filtered_obj:FO.Filtered_FoundNetBIOSHostnameWithSMB):
	network_obj = context['network']
	hostname = filtered_obj.get_hostname()

	auto_methods = []

	# if the hostname doesn't exist, create it.
	with TS.shared_lock:
		# retrieve or create the host object
		answer = network_obj.found_NetBIOS_hostname(hostname=hostname)

		host_obj = answer['object']
		auto_methods += answer['methods'] # only if it's a new host

		# activate smb methods
		auto_methods += host_obj.activate_smb_methods()

		print(f"hosts: {network_obj.hosts}")
		print(f"hostnames: {network_obj.hostnames}")

	return auto_methods


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

	auto_methods = []

	# with lock update the information on the netbios group
	with TS.shared_lock:
		nw_obj = ip_host.get_netbios_workstation_obj()
		if nw_obj is None:
			ip_host.add_role_netbios_workstation(hostname=None)
			nw_obj = ip_host.get_netbios_workstation_obj()
		auto_methods += nw_obj.add_group(group_obj)

	return auto_methods


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

	auto_methods = []

	with TS.shared_lock:
		nw_obj = host_obj.get_netbios_workstation_obj()
		if nw_obj is None:
			print("There was no network station obj for this ip")
		# get or create the group from the netbios workstation
		group_obj = nw_obj.get_group_from_group_id(netbios_group.lower()+'#'+'00')
		if group_obj is None:
			print("there was no group_obj with group id: {group_id} in the netbios workstation ")
		# update the roles 
		auto_methods += nw_obj.add_pdc_role_for_group(group_obj)

	return auto_methods



def update_components_found_new_domain_components_path_ldap(context_for_updates, filtered_obj):
	host_obj = context_for_updates['host']
	domain_components_path = filtered_obj.get_dc_path()

	auto_methods = []

	auto_methods += host_obj.check_if_ldap_domain_components_path_is_domain_path(domain_components_path)
	return auto_methods
	


def found_netbios_group(context_for_updates, filtered_obj):
	"""
	The components we update when we find a netbios group.
	We will create the netbios group object first, then 
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
	
	auto_methods = []

	with TS.shared_lock:
		# if we haven't found this group yet
		if not network_obj.check_if_netbios_group_exists(group_name, group_type):
			answer = network_obj.create_netbios_group(group_name, group_type)
			network_obj.associate_netbios_group_to_this_network(answer['object'])

			# associate the netbios group with an object (network, or Wins server)
			netbios_group_obj = answer['object'] 
			netbios_group_obj.associate_with_object(network_obj)

			# get the auto methods for netbios group found 
			answer['methods'] += [netbios_group_obj.auto_methods]
	return answer

		

def found_netbios_group_for_ip(context_for_updates, filtered_obj):
	auto_methods = list()
	
	# get the NetBIOSgroup object and the methods 
	answer = found_netbios_group(context_for_updates, filtered_obj)
	auto_methods += answer['methods']

	# update context for the next function
	context_for_next_func = context_for_updates
	context_for_next_func['group'] = answer['object'] # the group object we created

	# retrieve the host object from ip 
	network_obj = context_for_updates['network']
	ip = filtered_obj.get_ip()
	answer = check_ip_exists_retrieve_host_or_host_and_auto_methods(network_obj, ip)
	if answer['methods'] != []: # just for precaution
		auto_methods += answer['methods']
	ip_host = answer['object']

	# update context for next function 
	context_for_next_func['host'] = ip_host

	auto_methods += associate_existing_netbios_group_to_host_ip(context_for_next_func, filtered_obj)
	return auto_methods


def found_pdc_for_netbios_group(context, filtered_obj):
	network_obj = context['network']
	ip = filtered_obj.get_ip()

	auto_methods = []

	with TS.shared_lock:
		answer = check_ip_exists_retrieve_host_or_host_and_auto_methods(network_obj, ip)
		if answer['methods'] != []:
			auto_methods += answer['methods']
		ip_host = answer['object']

	context_for_function = context
	context_for_function['host'] = ip_host

	with TS.shared_lock:
		auto_methods += update_components_found_pdc_for_netbios_group(context_for_function, filtered_obj)

	return auto_methods


def found_netbios_hostname_with_smb_active(context, filtered_obj):
	"""
	What we do when we find a netbios hostsname with active SMB 
	DC1             <20> -         B <ACTIVE> 

	the hostname was already sent as a filtered obj, and so is created 
	for the host ip, that launched this command.
	"""
	network_obj = context['network']
	ip = filtered_obj.get_ip()

	auto_methods = []

	with TS.shared_lock:
		# retrieve the host object
		answer = check_ip_exists_retrieve_host_or_host_and_auto_methods(network_obj, ip)
		if answer['methods'] != []: # as precaution
			auto_methods += answer['methods']
		ip_host = answer['object']

		nw_obj = ip_host.get_netbios_workstation_obj()
		if nw_obj is None:
			print(f"No Netbios workstation for this host {ip}")
		auto_methods += nw_obj.add_netbios_smb_server()
		print(f"IP: {ip}")

	return auto_methods




"""
Update functions by method
"""

"""
THIS IS THE ONLY FUNCTION THAT THE CONTEXT WILL RECEIVE AN OBJECT. 
more specifically the root object, since it will always automaticallly run.
"""
def update_list_interfaces(context:dict, filtered_objects:list):
	# for this update the context will just be the root object
	if context['root'] is None:
		return 

	auto_methods = list()

	# context is only the root object
	root_obj = context['root']

	for filtered_obj in filtered_objects:
		# FOUND NEW INTERFACE
		if isinstance(filtered_obj, FO.Filtered_NewInterface):
			methods = update_components_found_new_interface(context, filtered_obj)
			auto_methods += methods

		# FOUND NEW NETWORK FOR AN INTERFACE
		elif isinstance(filtered_obj, FO.Filtered_NewNetworkForInterface):
			methods = update_components_found_new_network_for_interface(context, filtered_obj)
			auto_methods += methods

		# FOUND OUR IP
		elif isinstance(filtered_obj, FO.Filtered_FoundOurIPForNetwork):
			methods = update_components_found_our_ip_for_a_network(context, filtered_obj)
			auto_methods += methods

	# return the list of objects that are new
	return auto_methods




def update_ip_to_host_nbns(context, filtered_objects):
	# for this update the context will just be the root object
	if context['network'] is None or context['interface'] is None:
		return 

	auto_methods = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network']
	int_name = context['interface']

	# retrieve interface and network objects (both methods have locks)
	answer = check_exists_retrieve_interface_or_interface_and_auto_methods(int_name)
	int_obj = answer['object']
	answer = check_exists_retrieve_network_or_network_and_auto_methods(int_obj, net_name)
	net_obj = answer['object']

	context_for_updates = {'network':net_obj}

	auto_methods = list() # the list of new objects created

	host_obj = context['ip']
	for filtered_obj in filtered_objects:
		# FOUND HOSTNAME FOR IP
		if isinstance(filtered_obj, FO.Filtered_FoundNetBIOSHostnameForIP):
			print(f"filter found a hostname {filtered_obj.get_hostname()} for ip {filtered_obj.get_ip()}")
			auto_methods += update_components_found_NetBIOS_hostname_for_ip(context_for_updates, filtered_obj)

		# FOUND HOSTNAME WITH SMB ACTIVE - TODO 
		# this hostname might not yet exist in the network 
		if isinstance(filtered_obj, FO.Filtered_FoundNetBIOSHostnameWithSMB):
			print(f"filter foudn a hostname {filtered_obj.get_hostname()} using SMB")
			auto_methods += found_netbios_hostname_with_smb_active(context_for_updates, filtered_obj)
		
		# FOUND NETBIOS GROUP FOR IP 
		if isinstance(filtered_obj, FO.Filtered_FoundNetBIOSGroupForIP):
			print(f"filter found a group {filtered_obj.get_netbios_group()} for ip {filtered_obj.get_ip()}")
			auto_methods += found_netbios_group_for_ip(context_for_updates, filtered_obj)

		if isinstance(filtered_obj, FO.Filtered_FoundPDCIPForNetBIOSGroup):
			print(f"filter the ip {filtered_obj.get_ip()} is a PDC for {filtered_obj.get_netbios_group()}")
			auto_methods += found_pdc_for_netbios_group(context_for_updates, filtered_obj)
	
	return auto_methods




def update_arp_scan(context, filtered_objects):
	# for this update the context will just be the root object
	if context['network'] is None or context['interface'] is None:
		return 

	auto_methods = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network']
	int_name = context['interface']

	# retrieve interface and network objects (both methods have locks)
	answer = check_exists_retrieve_interface_or_interface_and_auto_methods(int_name)
	int_obj = answer['object']
	answer = check_exists_retrieve_network_or_network_and_auto_methods(int_obj, net_name)
	net_obj = answer['object']

	context_for_updates = {'network':net_obj}

	for filtered_obj in filtered_objects:
		# FOUND NEW IP
		if isinstance(filtered_obj, FO.Filtered_NewIPForNetwork):
			print(f"Found new IP {filtered_obj.get_ip()} in filter of ARP SCAN")
			auto_methods += update_components_found_new_ip_for_network(context_for_updates, filtered_obj)

	return auto_methods


def update_query_naming_context_of_dc_through_ldap(context, filtered_objects):
	"""
	does the update of network components from the information received 
	by the filter of the method, in the form of filtered objects

	TODO: 
	+ implemenent locks
	+ implement the proper functioning when the objects don't exist
	"""

	# for this update the context will just be the root object
	if context['network'] is None or context['interface'] is None or context['ip'] is None:
		return 

	auto_methods = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network']
	int_name = context['interface']
	host_name = context['ip']

	# retrieve interface and network objects (both methods have locks)
	answer = check_exists_retrieve_interface_or_interface_and_auto_methods(int_name)
	int_obj = answer['object']
	answer = check_exists_retrieve_network_or_network_and_auto_methods(int_obj, net_name)
	net_obj = answer['object']
	answer = check_ip_exists_retrieve_host_or_host_and_auto_methods(net_obj, host_name)
	host_obj = answer['object']

	context_for_updates = {'host': host_obj}

	for filtered_obj in filtered_objects:
		# FOUND A DOMAIN COMPONENTS PATH
		if isinstance(filtered_obj, FO.Filtered_DomainComponentsFromLDAPQuery):
			print(f"filter for ldap query found new domain components path {filtered_obj.get_dc_path()}")
			auto_methods += update_components_found_new_domain_components_path_ldap(context_for_updates, filtered_obj)

	return auto_methods


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

