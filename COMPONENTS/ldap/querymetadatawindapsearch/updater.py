from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from COMPONENTS.filteredobjects.filteredfounddefaultnamingcontext import Filtered_founddefaultnamingcontext
from COMPONENTS.filteredobjects.filteredfounddnshostname import Filtered_founddnshostname

from COMPONENTS.hosts.componentupdater import found_dns_hostname_for_host
from COMPONENTS.hosts.componentupdater import found_domain_for_dc_host


def query_metadata_windapsearch_updater(context:dict, filtered_objects:list):
	"""
	Updates the ldap components after we query the metadata through 
	windapsearch
	"""
	# retrieve interface and network objects (both methods have locks)
	with sharedvariables.shared_lock:
		int_name = context['interface_name']
		net_name = context['network_address']
		ip = context['ip']
		interface = sharedvariables.root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)
		host = network.get_ip_host_or_create_it(ip)
		ldap_server = host.get_ldap_server_obj(host)

	for filtered_obj in filtered_objects:
		# FOUND A DOMAIN COMPONENTS PATH
		if isinstance(filtered_obj, Filtered_founddnshostname):
			dns_hostname = filtered_obj.get_dns_hostname()
			host = ldap_server.get_host()
			logger.debug(f"filter of windapsearch metadata for ({host.ip}) \
       			found dns hostname {dns_hostname}")
   
			found_dns_hostname_for_host(host, dns_hostname)
			print(f'DNS hostname: {ldap_server.get_host().dns_hostname}')
			ldap_server.test = '2'
   
		if isinstance(filtered_obj, Filtered_founddefaultnamingcontext):
			host = ldap_server.get_host()
			default_nc = filtered_obj.get_naming_context()
			domain = sharedvariables.root_obj.get_or_create_domain(default_nc)
			logger.debug(f"filter of windapsearch metadata for ({host.get_ip()}) \
       			found he is a DC for domain with naming context: {default_nc}")

			found_domain_for_dc_host(host, domain)

	return 


			
	return 


