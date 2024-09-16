from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables
from COMPONENTS.filteredobjects.filteredfounddomaingroupforuserthroughrpc import Filtered_FoundDomainGroupForUserThroughRPC
from COMPONENTS.domains.componentupdater import found_group_rid_for_user_rid


def updateEnumDomainGroupsForUserThroughRPC(context:dict, filtered_objects:list):
	"""
	How we concatenate the information from the context 
	and the one received through the filters in order to update
	the components when we find a domain user in a domain group
	for a domain
	"""
	domain_name = context['domain_name']
	user_rid = context['user_rid'] # hex
 
	with sharedvariables.shared_lock:
		# get the domain
		domain = sharedvariables.root_obj.get_or_create_domain(domain_name)

		for filtered_obj in filtered_objects:
			# found domain user
			if isinstance(filtered_obj, Filtered_FoundDomainGroupForUserThroughRPC):
				logger.debug(f"filter for enum domain groups for user through rpc found group with rid ({filtered_obj.get_group_rid()}) for user rid ({user_rid})")

				group_rid = filtered_obj.get_group_rid() # hex
				found_group_rid_for_user_rid(domain=domain, user_rid=user_rid, group_rid=group_rid)

	return 
