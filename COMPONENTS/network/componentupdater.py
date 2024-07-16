from LOGGER.loggerconfig import logger
from THREADS.sharedvariables import shared_lock


def found_new_ip_for_network(network, ip):
	"""
	Defines the components we update when we find an IP 
	that is alive in a network

	we get or crerate the IP host.
	"""
	with shared_lock:
		logger.debug(f"updating components found new ip ({ip}) for network ({network.network_address})")
		host = network.get_ip_host_or_create_it(ip)
		return


def found_our_ip_for_a_network(interface_name, network_address, ip):
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
		if network is None: # not interested in this network TODO
			return 

		network.add_our_ip(ip)
		return 