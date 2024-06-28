import Methods
import ThreadShares as TS
import FilterObjects as FO
import NetworkComponentUpdater as NCU
from AbstractClasses import AbstractMethod
from LoggingConfig import logger


def init_root_object(obj):
	global root_obj 
	root_obj = obj



def update_list_interfaces(context:dict, filtered_objects:list):
	"""
	Defines the components we update when we list the interfaces available
	"""
	global root_obj

	for filtered_obj in filtered_objects:
		# FOUND NEW INTERFACE
		if isinstance(filtered_obj, FO.Filtered_NewInterface):
			interface_name = filtered_obj.get_interface_name()
			NCU.update_components_found_new_interface(interface_name)
			

		# FOUND NEW NETWORK FOR AN INTERFACE
		elif isinstance(filtered_obj, FO.Filtered_NewNetworkForInterface):
			interface_name = filtered_obj.get_interface_name()
			network_address = filtered_obj.get_network_address()
			NCU.update_components_found_new_network_for_interface(interface_name, network_address)

		# FOUND OUR IP
		elif isinstance(filtered_obj, FO.Filtered_FoundOurIPForNetwork):
			interface_name = filtered_obj.get_interface_name()
			network_address = filtered_obj.get_network_address()
			ip = filtered_obj.get_ip()
			NCU.update_components_found_our_ip_for_a_network(interface_name, network_address, ip)
	return 




def update_ip_to_host_nbns(context, filtered_objects):
	global root_obj

	# some mistake 
	if context['network_address'] is None or context['interface_name'] is None:
		return 

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']

	# retrieve interface and network objects (both methods have locks)
	interface = root_obj.get_interface_or_create_it(int_name)
	network = interface.get_network_or_create_it(net_name)

	for filtered_obj in filtered_objects:
		# FOUND HOSTNAME FOR IP
		if isinstance(filtered_obj, FO.Filtered_FoundNetBIOSHostnameForIP):
			logger.debug(f"filter found a hostname {filtered_obj.get_hostname()} for ip {filtered_obj.get_ip()}")
			hostname = filtered_obj.get_hostname()
			ip = filtered_obj.get_ip()
			NCU.update_components_found_NetBIOS_hostname_for_ip(network, hostname, ip)

		# FOUND HOSTNAME WITH SMB ACTIVE - TODO 
		# this hostname might not yet exist in the network 
		elif isinstance(filtered_obj, FO.Filtered_FoundNetBIOSHostnameWithSMB):
			logger.debug(f"filter foudn a hostname {filtered_obj.get_hostname()} using SMB")
			ip = filtered_obj.get_ip()
			NCU.update_components_found_netbios_hostname_with_smb_active(network, ip)
		
		# FOUND NETBIOS GROUP FOR IP 
		elif isinstance(filtered_obj, FO.Filtered_FoundNetBIOSGroupForIP):
			logger.debug(f"filter found a group {filtered_obj.get_netbios_group()} for ip {filtered_obj.get_ip()}")
			group_name = filtered_obj.get_netbios_group()
			group_type = filtered_obj.get_type()
			ip = filtered_obj.get_ip()
			NCU.update_components_found_netbios_group_for_ip(network, ip, group_name, group_type)

		elif isinstance(filtered_obj, FO.Filtered_FoundPDCIPForNetBIOSGroup):
			logger.debug(f"filter the ip {filtered_obj.get_ip()} is a PDC for {filtered_obj.get_netbios_group()}")
			ip = filtered_obj.get_ip()
			netbios_group = filtered_obj.get_netbios_group()
			NCU.update_components_found_pdc_for_netbios_group(network, ip, netbios_group)
	return 




def update_arp_scan(context, filtered_objects):
	global root_obj

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None:
		return 

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']

	# retrieve interface and network objects (both methods have locks)
	interface = root_obj.get_interface_or_create_it(int_name)
	network = interface.get_network_or_create_it(net_name)

	for filtered_obj in filtered_objects:
		# FOUND NEW IP
		if isinstance(filtered_obj, FO.Filtered_NewIPForNetwork):
			logger.debug(f"Found new IP ({filtered_obj.get_ip()}) for network ({network.network_address})")
			ip = filtered_obj.get_ip()
			NCU.update_components_found_new_ip_for_network(network, ip)
	return


def update_query_root_dse_of_dc_through_ldap(context, filtered_objects):
	"""
	updates the components when we find a naminc context through 
	ldap 

	TODO: 
	+ implemenent locks
	+ implement the proper functioning when the objects don't exist
	"""
	global root_obj

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None or context['ip'] is None:
		return 

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_name = context['ip']

	# retrieve interface and network objects (both methods have locks)
	interface = root_obj.get_interface_or_create_it(int_name)
	network = interface.get_network_or_create_it(net_name)
	if network is None: # not interested in this network
		return 
	host = network.get_ip_host_or_create_it(context['ip'])

	for filtered_obj in filtered_objects:
		# FOUND A DOMAIN COMPONENTS PATH
		if isinstance(filtered_obj, FO.Filtered_DomainComponentsFromLDAPQuery):
			logger.debug(f"filter for ldap query to ip ({host.ip}) found new root domain path {filtered_obj.get_dc_path()}")

			domain_components_path = filtered_obj.get_dc_path()
			NCU.update_components_found_new_domain_components_path_ldap(host, domain_components_path)


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

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_ip = context['ip']

	interface = root_obj.get_interface_or_create_it(int_name)
	network = interface.get_network_or_create_it(net_name)
	if network is None: # not interested in this network
		return 
	host = network.get_ip_host_or_create_it(host_ip)

	for filtered_obj in filtered_objects:
		# FOUND smb service was up
		if isinstance(filtered_obj, FO.Filtered_SMBServiceIsUp):
			logger.debug(f"filter for checking if smb service is up for ip ({host.get_ip()}) found that it IS UP")

			smb_port = filtered_obj.get_port()
			NCU.update_components_found_smb_service_is_running(host, smb_port)
			return 



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

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_ip = context['ip']

	interface = root_obj.get_interface_or_create_it(int_name)
	network = interface.get_network_or_create_it(net_name)
	if network is None: # not interested in this network
		return 
	host = network.get_ip_host_or_create_it(host_ip)

	for filtered_obj in filtered_objects:
		# FOUND MSRPC is up
		if isinstance(filtered_obj, FO.Filtered_MSRPCServiceIsUp):
			logger.debug(f"filter for checking if msrpc service is up for ip ({host.get_ip()}) found that it IS UP")

			msrpc_port = filtered_obj.get_port()
			NCU.update_components_found_msrpc_service_is_running(host, msrpc_port)
	return 


def update_enum_domain_trusts_through_rpc(context:dict, filtered_objects:list):
	global root_obj

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None or context['ip'] is None:
		return 

	auto_functions = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_ip = context['ip']

	interface = root_obj.get_interface_or_create_it(int_name)
	network = interface.get_network_or_create_it(net_name)
	if network is None: # not interested in this network
		return 
	host = network.get_ip_host_or_create_it(host_ip)


	for filtered_obj in filtered_objects:
		# FOUND domain trust
		if isinstance(filtered_obj, FO.Filtered_FoundDomainTrust):
			logger.debug(f"filter for enum domain trusts through rpc ({host.get_ip()}) found that trust to ({filtered_obj.get_domain_name()})")

			trusting_domain = context['domain_name']
			trusted_domain = filtered_obj.get_domain_name()
			NCU.update_components_found_domain_trust(trusting_domain, trusted_domain)
	return 
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
	elif method._name == 'query root dse of DC through LDAP':
		return update_query_root_dse_of_dc_through_ldap(context, filtered_objects)
	elif method._name == 'check if SMB service is running':
		return update_check_if_smb_service_is_running(context, filtered_objects)
	elif method._name == 'check if MSRPC service is running':
		return update_check_if_msrpc_service_is_running(context, filtered_objects)
	elif method._name == 'dump interface endpoints from endpoint mapper':
		return [] # nothing for now 
	elif method._name == 'enum domains trusts through rpc':
		return update_enum_domain_trusts_through_rpc(context, filtered_objects)