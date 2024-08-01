from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as sharedvariables

from COMPONENTS.filteredobjects.filteredfounddistinguishednamefordomainuser import Filtered_FoundDistinguishedNameForDomainUser
from COMPONENTS.filteredobjects.filteredfounduserprincipalnamefordomainuser import Filtered_FoundUserPrincipalNameForDomainUser
from COMPONENTS.domains.componentupdater import found_distinguished_name_for_sam_account_name
from COMPONENTS.domains.componentupdater import found_user_principal_name_for_sam_account_name

def retrieve_list_users_with_windapsearch_updater(context:dict, filtered_objects:list):
	"""
 	Updates the components for when we find user information
  	through windapsearch.
   	"""
	with sharedvariables.shared_lock:
		domain_name = context['domain_name']
		domain = sharedvariables.root_obj.get_or_create_domain(domain_name)

		for fo in filtered_objects:
			if isinstance(fo, Filtered_FoundDistinguishedNameForDomainUser):
				username = fo.get_sam_account_name()
				distinguished_name = fo.get_distinguished_name()	
				logger.debug(f"Filter foud distinguished name ({distinguished_name})\
        for user ({username})")
				found_distinguished_name_for_sam_account_name(domain, username, distinguished_name)

			"""	
			if isinstance(fo, Filtered_FoundUserPrincipalNameForDomainUser):
				username = fo.get_sam_account_name()
				user_principal_name = fo.get_user_principal_name()
				logger.debug(f"Filter found user principal name ({user_principal_name})\
        for user ({username})")
				found_user_principal_name_for_sam_account_name(domain, username, user_principal_name)
			"""
	return 