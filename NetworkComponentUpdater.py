

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
def update_components_found_new_interface(interface_name):
	"""
	What we do when filter found a Filtered object
	of type filtered_newinterface

	returns dict 'object' and 'methods' (if a new
	interface network component was created)
	"""
	global root_obj

	# in every situation where you mess with an object you check if anything changes

	with TS.shared_lock:
		logger.debug(f"interface: ({interface_name}) found -> updating components")
		
		interface = root_obj.get_interface_or_create_it(interface_name) # already calls the methods
		return 




def update_components_found_new_network_for_interface(interface_name, network_address):
	"""
	What we do when we receive a filtered_new_network_for_interface

	we get or create the interface.
	And for that interface we get or create the network.

	returns a dict with 'object' and 'methods' (if we created
	a new network or interface objects)
	"""
	global root_obj

	with TS.shared_lock:
		logger.debug(f"network ({network_address}) for interface ({interface_name}) found -> updating components")
		
		interface = root_obj.get_interface_or_create_it(interface_name)

		# ASKS THE USER IF HE WANTS THIS NETWORK
		network = interface.get_network_or_create_it(network_address)
		return 





def update_components_found_our_ip_for_a_network(interface_name, network_address, ip):
	"""
	Defines what components we update when we find OUR
	IP for a particular network

	gets or creates the interface
	gets or creates the network for the interface
	updates the network component to have our ip 
	"""
	global root_obj
	auto_functions = []


	# LOCK
	with TS.shared_lock:
		interface = root_obj.get_interface_or_create_it(interface_name)
		
		network = interface.get_network_or_create_it(network_address)

		network.add_our_ip(ip)
		return 


def update_components_found_NetBIOS_hostname_for_ip(network, hostname, ip):
	"""
	Defines the componets we update when we find a netbios
	hostname for a host with an IP.

	we get or create a Netbios_worstation role for that ip, 
	with the hostname we found.
	"""
	with TS.shared_lock:
		network.associate_netbios_workstation_to_ip_host_through_hostname(hostname, ip)
		return 


def update_components_found_netbios_hostname_with_smb_active(network, ip):
	"""
	What we do when we find a netbios hostsname with active SMB 
	DC1             <20> -         B <ACTIVE> 

	the hostname was already sent as a filtered obj, and so is created 
	for the host ip, that launched this command.
	"""

	with TS.shared_lock:
		# retrieve the host object
		host = network.get_ip_host_or_create_it(ip)
		if host is None: # if it's 'our' ip
			return 

		netbios_ws = host.get_netbios_workstation_obj()
		if netbios_ws is None: # if there wasn't a netbios workstation for the host
			return 
		
		netbios_ws.add_netbios_smb_server()

	return


def update_components_found_netbios_group(network, group_name, group_type):
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
	with TS.shared_lock:
		# only do something if it's a NEW group
		if not network.check_if_netbios_group_exists(group_name, group_type):
			# create the group network component
			netbios_group = network.create_netbios_group(group_name, group_type)

			# associate the netbios group to the network 
			network.associate_netbios_group_to_this_network(netbios_group)

			# associate the netbios group with an object (network, or Wins server)
			netbios_group.associate_with_object(network)
	return netbios_group

		

def update_components_found_netbios_group_for_ip(network, ip, group_name, group_type):
	"""
	Defines the components we update when we find a netbios group
	for an ip.
	The group may not yet exist in our objects. 
	The ip may also not exist
	"""
	with TS.shared_lock:
		# get the NetBIOSgroup object and the methods 
		netbios_group = update_components_found_netbios_group(network, group_name, group_type)

		# retrieve the host object from ip 
		host = network.get_ip_host_or_create_it(ip)

		host.associate_existing_netbios_group_to_host_ip(netbios_group)
		return


def update_components_found_pdc_for_netbios_group(network, ip, netbios_group):
	"""
	Checks if the ip already is associated with a 
	"""

	with TS.shared_lock:
		host = network.get_ip_host_or_create_it(ip)

		# get the netbios worksation
		netbios_ws = host.get_netbios_workstation_obj()
		if netbios_ws is None:
			logger.debug(f"There was no network station obj for this ip ({host.get_ip()})")
			return 

		# get or create the group from the netbios workstation
		netbios_group = netbios_ws.get_group_from_group_id(netbios_group.lower()+'#'+'00')
		if netbios_group is None:
			logger.debug(f"there was no netbios group with group id: {netbios_group.lower()+'#'+'00'} in the netbios workstation ")
		
		# update the roles in the netbios workstation
		netbios_ws.add_pdc_role_for_group(netbios_group)
	return 


def update_components_found_new_ip_for_network(network, ip):
	"""
	Defines the components we update when we find an IP 
	that is alive in a network

	we get or crerate the IP host.
	"""
	with TS.shared_lock:
		logger.debug(f"updating components found new ip ({ip}) for network ({network.network_address})")
		host = network.get_ip_host_or_create_it(ip)
		return


def update_components_found_new_domain_components_path_ldap(host, domain_components_path):
	"""
	Updates the network components for the event of finding new 
	domain components path through ldap. 
	We found a ldap server and we might have found a Domain Controller's domain name.

	+ we received a filtered object from the filter it means that the 
	service is on. Which means this host (if it doesn't have already) 
	must have an ldap service associated. 
	+ gets/creates the ldap server for the host
	+ associates the domain to the host
	+ add's this host as a DC to the domain

	Next we must check if any of the names corresponds to a domain name
	"""
	global root_obj

	with TS.shared_lock:
		# create or get the ldap server role for this host
		ldap_server = host.get_or_add_role_ldap_server()

		# check if the domain exists in the root database
		domain = root_obj.get_or_create_domain(domain_components_path)
		
		# there is only 1 domain for each host
		# put the host as a dependent object of the domain.
		host.associate_domain_to_host_if_not_already(domain) 

		# put this host as a DC for the domain
		domain.add_dc(ldap_server)
	return



def update_components_found_smb_service_is_running(host, port):
	"""
	Updates the components when we find that an smb service is running
	for a host
	"""
	smb_server = host.found_smb_service_running_on_port(port)
	return


def update_components_found_msrpc_service_is_running(host, port):
	"""
	Updates the components when we find that a msrpc service is running 
	for a host
	"""
	msrpc_server = host.found_msrpc_service_running_on_port(port)
	return



def update_components_found_domain_trust(trusting_domain_name, trusted_domain_name):
	"""
	Updates components when a domain trust is found.

	checks if the domains are already present in the databse,
	updates also their trust relationships
	"""
	global root_obj

	with TS.shared_lock:
		# check if the trusting domain exists in the root database
		trusting_domain = root_obj.get_or_create_domain(trusting_domain_name)

		# same domains trusting = trusted
		if trusting_domain_name == trusted_domain_name: 
			# no need to add, since they are the same
			return

		# get or create the trusted domain
		trusted_domain_name = root_obj.get_or_create_domain(trusted_domain_name)

		# update the thrusts
		trusting_domain.add_domain_trust(trusted_domain)
		return auto_functions