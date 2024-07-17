from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables


from COMPONENTS.netbios.componentupdater import found_netbios_hostname_for_ip
from COMPONENTS.netbios.componentupdater import found_netbios_hostname_with_smb_active
from COMPONENTS.netbios.componentupdater import found_pdc_for_netbios_group
from COMPONENTS.netbios.componentupdater import found_netbios_group_for_ip

from COMPONENTS.filteredobjects.filteredfoundnetbioshostnameforip import Filtered_FoundNetBIOSHostnameForIP
from COMPONENTS.filteredobjects.filteredfoundnetbioshostnamewithsmb import Filtered_FoundNetBIOSHostnameWithSMB
from COMPONENTS.filteredobjects.filteredfoundnetbiosgroupforip import Filtered_FoundNetBIOSGroupForIP
from COMPONENTS.filteredobjects.filteredfoundpdcipfornetbiosgroup import Filtered_FoundPDCIPForNetBIOSGroup


def update_ip_to_host_nbns(context, filtered_objects):

	# some mistake 
	if context['network_address'] is None or context['interface_name'] is None:
		return 

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']

	# retrieve interface and network objects (both methods have locks)
	with sharedvariables.shared_lock:
		interface = sharedvariables.root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)

	for filtered_obj in filtered_objects:
		# FOUND HOSTNAME FOR IP
		if isinstance(filtered_obj, Filtered_FoundNetBIOSHostnameForIP):
			logger.debug(f"filter found a hostname {filtered_obj.get_hostname()} for ip {filtered_obj.get_ip()}")
			hostname = filtered_obj.get_hostname()
			ip = filtered_obj.get_ip()
			found_netbios_hostname_for_ip(network, hostname, ip)

		# FOUND HOSTNAME WITH SMB ACTIVE - TODO 
		# this hostname might not yet exist in the network 
		elif isinstance(filtered_obj, Filtered_FoundNetBIOSHostnameWithSMB):
			logger.debug(f"filter foudn a hostname {filtered_obj.get_hostname()} using SMB")
			ip = filtered_obj.get_ip()
			found_netbios_hostname_with_smb_active(network, ip)
		
		# FOUND NETBIOS GROUP FOR IP 
		elif isinstance(filtered_obj, Filtered_FoundNetBIOSGroupForIP):
			logger.debug(f"filter found a group {filtered_obj.get_netbios_group()} for ip {filtered_obj.get_ip()}")
			group_name = filtered_obj.get_netbios_group()
			group_type = filtered_obj.get_type()
			ip = filtered_obj.get_ip()
			found_netbios_group_for_ip(network, ip, group_name, group_type)

		elif isinstance(filtered_obj, Filtered_FoundPDCIPForNetBIOSGroup):
			logger.debug(f"filter the ip {filtered_obj.get_ip()} is a PDC for {filtered_obj.get_netbios_group()}")
			ip = filtered_obj.get_ip()
			netbios_group = filtered_obj.get_netbios_group()
			found_pdc_for_netbios_group(network, ip, netbios_group)
	return 