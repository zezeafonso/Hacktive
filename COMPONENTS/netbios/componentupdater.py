from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables


def found_netbios_hostname_with_smb_active(network, ip):
	"""
	What we do when we find a netbios hostsname with active SMB 
	DC1             <20> -         B <ACTIVE> 

	the hostname was already sent as a filtered obj, and so is created 
	for the host ip, that launched this command.
	"""

	with sharedvariables.shared_lock:
		# retrieve the host object
		host = network.get_ip_host_or_create_it(ip)
		if host is None: # if it's 'our' ip
			return 

		netbios_ws = host.get_netbios_workstation_obj()
		if netbios_ws is None: # if there wasn't a netbios workstation for the host
			return 
		
		netbios_ws.add_netbios_smb_server()

	return


def found_netbios_group(network, group_name, group_type):
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
	with sharedvariables.shared_lock:
		# only do something if it's a NEW group
		if not network.check_if_netbios_group_exists(group_name, group_type):
			# create the group network component
			netbios_group = network.create_netbios_group(group_name, group_type)

			# associate the netbios group to the network 
			network.associate_netbios_group_to_this_network(netbios_group)

			# associate the netbios group with an object (network, or Wins server)
			netbios_group.associate_with_object(network)
	return netbios_group


def found_netbios_group_for_ip(network, ip, group_name, group_type):
	"""
	Defines the components we update when we find a netbios group
	for an ip.
	The group may not yet exist in our objects. 
	The ip may also not exist
	"""
	with sharedvariables.shared_lock:
		# get the NetBIOSgroup object and the methods 
		netbios_group = found_netbios_group(network, group_name, group_type)

		# retrieve the host object from ip 
		host = network.get_ip_host_or_create_it(ip)

		host.associate_existing_netbios_group_to_host_ip(netbios_group)
		return


def found_pdc_for_netbios_group(network, ip, netbios_group):
	"""
	Checks if the ip already is associated with a 
	"""

	with sharedvariables.shared_lock:
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


def found_netbios_hostname_for_ip(network, hostname, ip):
	"""
	Defines the componets we update when we find a netbios
	hostname for a host with an IP.

	we get or create a Netbios_worstation role for that ip, 
	with the hostname we found.
	"""
	with sharedvariables.shared_lock:
		network.associate_netbios_workstation_to_ip_host_through_hostname(hostname, ip)
		return 