from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables


from COMPONENTS.filteredobjects.filteredfoundmsparininterfaces import Filtered_FoundMSPARInInterfaces


# TODO
def update(context:dict, filtered_objects:list):
    # for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None or context['ip'] is None:
		return 

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_name = context['ip']

	# retrieve interface and network objects (both methods have locks)
	with sharedvariables.shared_lock:
		interface = sharedvariables.root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)
		if network is None: # not interested in this network
			return 
		host = network.get_ip_host_or_create_it(context['ip'])
	
	# Domain components must be first so we can add first the LDAP server 
	# to the host, so we can then do the other operations.
	for filtered_obj in filtered_objects:
		if isinstance(filtered_obj, Filtered_FoundMSPARInInterfaces):
			msrpc_server = host.get_or_add_role_rpc_server()
   
			msrpc_server.add_interface_of_interest('MS_PAR')
