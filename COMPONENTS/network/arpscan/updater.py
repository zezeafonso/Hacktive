from LOGGER.loggerconfig import logger
from THREADS.sharedvariables import shared_lock, root_obj
from COMPONENTS.filteredobjects.filterednewipfornetwork import Filtered_NewIPForNetwork
from COMPONENTS.network.componentupdater import found_new_ip_for_network



def update_arp_scan(context, filtered_objects):

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None:
		return 

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']

	with shared_lock:
		# retrieve interface and network objects (both methods have locks)
		interface = root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)

	for filtered_obj in filtered_objects:
		# FOUND NEW IP
		if isinstance(filtered_obj, Filtered_NewIPForNetwork):
			logger.debug(f"Found new IP ({filtered_obj.get_ip()}) for network ({network.network_address})")
			ip = filtered_obj.get_ip()
			found_new_ip_for_network(network, ip)
	return