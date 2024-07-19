from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables
from COMPONENTS.filteredobjects.filteredfounddomainuserforgroupthroughrpc import Filtered_FoundDomainUserForGroupThroughRPC
from COMPONENTS.domains.componentupdater import found_user_rid_belonging_to_group_rid


def updateEnumDomainUsersInGroupThroughRPC(context:dict, filtered_objects:list):
	"""
	How we concatenate the information from the context 
	and the one received through the filters in order to update
	the components when we find a domain user in a domain group
	for a domain
	"""
	with sharedvariables.shared_lock:
		domain_name = context['domain_name']
		group_rid = context['group_rid']
  
		domain = sharedvariables.root_obj.get_or_create_domain(domain_name)

		for filtered_obj in filtered_objects:
			# found domain user
			if isinstance(filtered_obj, Filtered_FoundDomainUserForGroupThroughRPC):
				logger.debug(f"filter for enum domain users through rpc found user with rid ({filtered_obj.get_user_rid()}) for group rid ({group_rid})")

				user_rid = filtered_obj.get_user_rid()
				found_user_rid_belonging_to_group_rid(domain=domain, group_rid=group_rid, user_rid=user_rid)

	return 
