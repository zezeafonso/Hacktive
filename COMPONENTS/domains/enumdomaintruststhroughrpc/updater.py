from LOGGER.loggerconfig import logger

from THREADS.sharedvariables import shared_lock, root_obj


from COMPONENTS.filteredobjects.filteredfounddomaintrust import Filtered_FoundDomainTrust
from COMPONENTS.domains.componentupdater import found_domain_trust


def update_enum_domain_trusts_through_rpc(context:dict, filtered_objects:list):

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None or context['ip'] is None:
		return 

	auto_functions = list() # the list of new objects created

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_ip = context['ip']

	with shared_lock:
		interface = root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)
		if network is None: # not interested in this network
			return 
		host = network.get_ip_host_or_create_it(host_ip)


	for filtered_obj in filtered_objects:
		# FOUND domain trust
		if isinstance(filtered_obj, Filtered_FoundDomainTrust):
			logger.debug(f"filter for enum domain trusts through rpc ({host.get_ip()}) belonging to domain ({context['domain_name']}) found that trust to ({filtered_obj.get_domain_name()})")

			trusting_domain_name = context['domain_name']
			trusted_domain_name = filtered_obj.get_domain_name()
			found_domain_trust(trusting_domain_name, trusted_domain_name)
	return 

