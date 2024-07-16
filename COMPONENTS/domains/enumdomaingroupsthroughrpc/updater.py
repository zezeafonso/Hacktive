from LOGGER.loggerconfig import logger
from THREADS.sharedvariables import shared_lock, root_obj
from COMPONENTS.filteredobjects.filteredfounddomaingroupthroughrpc import Filtered_FoundDomainGroupThroughRPC
from COMPONENTS.domains.componentupdater import found_group_for_domain



def update_enum_domain_groups_through_rpc(context:dict, filtered_objects:list):
	# we need to know the domain
	domain_name = context['domain_name']
	if domain_name is None:
		return 

	with shared_lock:
		domain = root_obj.get_or_create_domain(domain_name)
  
	for filtered_obj in filtered_objects:
		if isinstance(filtered_obj, Filtered_FoundDomainGroupThroughRPC):
			groupname = filtered_obj.get_group()
			rid = filtered_obj.get_rid()

			logger.debug(f"filter for enum domain groups through rpc found group ({groupname}) with rid ({rid})")
			found_group_for_domain(domain, groupname, rid)

	return 