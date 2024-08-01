from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

import COMPONENTS.smb.componentupdater as smb_componentupdater
from COMPONENTS.filteredobjects.filteredfoundsmbservicesigning import Filtered_FoundSMBServiceSigning
from COMPONENTS.filteredobjects.filteredfoundsmbv1value import Filtered_FoundSMBv1Value
from COMPONENTS.filteredobjects.filteredfounddomainofmachine import Filtered_FoundDomainOfMachine

def BasicCrackMapExec_Updater(context:dict, filtered_objects:list):
	"""
 	Receives the filtered objects from output parsing 
  	and the context from the method
   	"""
	with sharedvariables.shared_lock:
		ip = context['ip']
		net_name = context['network_address']
		int_name = context['interface_name']
  
		interface = sharedvariables.root_obj.get_interface_or_create_it(int_name)
		network = interface.get_network_or_create_it(net_name)
		host = network.get_ip_host_or_create_it(ip)
		smb_server = host.get_smb_server_obj()
		
		if smb_server is None:
			return
		
  
		for filtered_obj in filtered_objects:
			# found domain
			if isinstance(filtered_obj, Filtered_FoundDomainOfMachine):
				domain_name = filtered_obj.get_domain_name()
				logger.debug(f"Filter for basic CME found domain\
        			({domain_name}) for machine ip ({ip})")
				# TODO
				smb_componentupdater.found_domain_name_for_smb_server(domain_name, smb_server)
				
			# found smbv1 required or not
			if isinstance(filtered_obj, Filtered_FoundSMBv1Value):
				smbv1_value = filtered_obj.get_smbv1_value()
				logger.debug(f"Filter for basic CME found \
        			SMBv1 requirement is ({smbv1_value}) for ({ip})")
				smb_server.update_smbv1_value(smbv1_value)
				
			if isinstance(filtered_obj, Filtered_FoundSMBServiceSigning):
				signing = filtered_obj.get_signing_value()
				logger.debug(f"Filter for basic CME found signing \
        			requirement is ({signing}) for ({ip})")
				smb_server.update_signing_required_value(signing)
	return 
