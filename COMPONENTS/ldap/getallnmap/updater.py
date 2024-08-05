from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from COMPONENTS.filteredobjects.filteredfounddomainuserattribute import Filtered_FoundDomainUserAttribute
from COMPONENTS.filteredobjects.filteredfounddomaingroupattribute import Filtered_FoundDomainGroupAttribute


def get_all_ldap_updater(context:dict, filtered_objects:list):
	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_name = context['ip']
	domain_name = context['domain_name']

	# retrieve interface and network objects (both methods have locks)
	with sharedvariables.shared_lock:
		interface = sharedvariables.root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)
		if network is None: # not interested in this network
			return 
		host = network.get_ip_host_or_create_it(host_name)
		domain = sharedvariables.root_obj.get_or_create_domain(domain_name)


	# for every attribute of 
	for filtered_obj in filtered_objects:
		# supported ldap version
		if isinstance(filtered_obj, Filtered_FoundDomainUserAttribute):
			username = filtered_obj.get_username()
			attr_name = filtered_obj.get_attr_name()
			attr_val = filtered_obj.get_attr_value()
			domain_user = domain.get_or_create_user_from_username(username)
			logger.debug(f"Filter found attribute ({attr_name}) with value\
       ({attr_val}) for user with username ({username})")

			domain_user.add_attribute(attr_name, attr_val)
   
		if isinstance(filtered_obj, Filtered_FoundDomainGroupAttribute):
			groupname = filtered_obj.get_groupname()
			attr_name = filtered_obj.get_attr_name()
			attr_val = filtered_obj.get_attr_value()
			domain_group = domain.get_or_create_group_from_groupname(groupname)
			logger.debug(f"Filter found attribute ({attr_name}) with value\
       ({attr_val}) for user with username ({groupname})")
	
			domain_group.add_attribute(attr_name, attr_val)
	return