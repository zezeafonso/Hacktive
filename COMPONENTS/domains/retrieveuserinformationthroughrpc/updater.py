from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables
from COMPONENTS.filteredobjects.filteredfounddomainuserridthroughrpc import Filtered_FoundDomainUserRidThroughRPC
from COMPONENTS.domains.componentupdater import found_user_rid_for_username


def update_retrieve_information_through_rpc(context:dict, filtered_objects:list):
    
	with sharedvariables.shared_lock:
		domain_name = context['domain_name']
		username = context['username']
		domain = sharedvariables.root_obj.get_or_create_domain(domain_name)
  
		for filtered_obj in filtered_objects:
			# found domain user
			if isinstance(filtered_obj, Filtered_FoundDomainUserRidThroughRPC):
				logger.debug(f"filter for retrieving information of username ({username}) found its rid ({filtered_obj.get_user_rid()})")

				user_rid = filtered_obj.get_user_rid()
				found_user_rid_for_username(domain, username, user_rid)

	return 