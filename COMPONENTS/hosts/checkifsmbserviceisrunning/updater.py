from LOGGER.loggerconfig import logger
from COMPONENTS.hosts.componentupdater import update_components_found_smb_service_is_running
from COMPONENTS.filteredobjects.filteredfoundsmbserviceisup import Filtered_FoundSMBServiceIsUp
import THREADS.sharedvariables as sharedvariables


def update_check_if_smb_service_is_running(context:dict, filtered_objects:list):
	"""
	Defines the components we update when we find that a host
	is running a SMB service

	get the interface; get network; get host
	if host doesn't have already information that is running SMB
		add it.
	"""

	# for this update the context will just be the root object
	if context['network_address'] is None or context['interface_name'] is None or context['ip'] is None:
		return 

	# context is only the network and interface names
	net_name = context['network_address']
	int_name = context['interface_name']
	host_ip = context['ip']

	with sharedvariables.shared_lock:
		interface = sharedvariables.root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)
		if network is None: # not interested in this network
			return 
		host = network.get_ip_host_or_create_it(host_ip)

	for filtered_obj in filtered_objects:
		# FOUND smb service was up
		if isinstance(filtered_obj, Filtered_FoundSMBServiceIsUp):
			logger.debug(f"filter for checking if smb service is up for ip ({host.get_ip()}) found that it IS UP")

			smb_port = filtered_obj.get_port()
			update_components_found_smb_service_is_running(host, smb_port)
			return 

