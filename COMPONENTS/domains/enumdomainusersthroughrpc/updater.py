from LOGGER.loggerconfig import logger
from THREADS.sharedvariables import shared_lock
from THREADS.sharedvariables import root_obj
from COMPONENTS.filteredobjects.filteredfounddomainuserthroughrpc import Filtered_FoundDomainUserThroughRPC
from COMPONENTS.domains.componentupdater import found_user_for_domain


def update_enum_domain_users_through_rpc(context:dict, filtered_objects:list):

	# we need to know the domain 
	if context['domain_name'] is None:
		return 

	with shared_lock:
		domain = root_obj.get_or_create_domain(context['domain_name'])
	for filtered_obj in filtered_objects:
		# found domain user
		if isinstance(filtered_obj, Filtered_FoundDomainUserThroughRPC):
			logger.debug(f"filter for enum domain users through rpc found user ({filtered_obj.get_user()}) with rid ({filtered_obj.get_rid()})")

			username = filtered_obj.get_user()
			rid = filtered_obj.get_rid()
			found_user_for_domain(domain, username, rid)

	return 