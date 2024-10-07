from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables
from COMPONENTS.filteredobjects.filteredfounddomainsid import Filtered_FoundDomainSID
from COMPONENTS.domains.componentupdater import found_user_for_domain


def update_retrieve_domain_sid_through_rpc(context:dict, filtered_objects:list):

	# we need to know the domain 
	if context['domain_name'] is None:
		return 

	with sharedvariables.shared_lock:
		domain_name = context['domain_name']
		domain = sharedvariables.root_obj.get_or_create_domain(domain_name)
  
		for filtered_obj in filtered_objects:
			# found domain user
			if isinstance(filtered_obj, Filtered_FoundDomainSID):
				logger.debug(f"filter for retrievedomainsidthroughrpc recieved domain sid: ({filtered_obj.get_sid()})")

				domain_sid = filtered_obj.get_sid()
				domain.add_domain_sid(domain_sid)
				

	return 