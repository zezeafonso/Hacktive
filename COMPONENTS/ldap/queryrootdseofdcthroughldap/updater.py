from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from COMPONENTS.ldap.componentupdater import found_new_domain_components_path_ldap
from COMPONENTS.filteredobjects.filteredfounddomaincomponentsfromldapquery import Filtered_FoundDomainComponentsFromLDAPQuery
from COMPONENTS.filteredobjects.filteredfounddnshostname import Filtered_founddnshostname
from COMPONENTS.filteredobjects.filteredfoundsupportedldapversion import Filtered_FoundSupportedLdapVersion

from COMPONENTS.hosts.componentupdater import found_dns_hostname_for_host

def update_query_root_dse_of_dc_through_ldap(context, filtered_objects):
	"""
	updates the components when we find a naminc context through 
	ldap 

	TODO: 
	+ implement the proper functioning when the objects don't exist
	"""
	
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

	for filtered_obj in filtered_objects:
		# domain components path
		if isinstance(filtered_obj, Filtered_FoundDomainComponentsFromLDAPQuery):
			logger.debug(f"filter for ldap query to ip ({host.ip}) found new root domain path {filtered_obj.get_dc_path()}")

			domain_components_path = filtered_obj.get_dc_path()
			found_new_domain_components_path_ldap(host, domain_components_path)

		# dns hostname
		if isinstance(filtered_obj, Filtered_founddnshostname):
			dns_hostname = filtered_obj.get_dns_hostname()
			logger.debug(f"Filter for ldap root dse query to ({host.ip})\
       found the dnshostname ({dns_hostname})")
	
			found_dns_hostname_for_host(host, dns_hostname)

		# supported ldap version
		if isinstance(filtered_obj, Filtered_FoundSupportedLdapVersion):
			version = filtered_obj.get_version()
			ldap_server = host.get_ldap_server_obj() # mandatory otherwise this method wouldn't ahve been launched
			logger.debug(f"Filter found supported version ({version})\
       for host ({host.get_ip()})")

			ldap_server.add_supported_version(version)

