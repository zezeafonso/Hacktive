"""
NCU.update_components_found_group_for_domain(domain, groupname, rid)
NCU.update_components_found_user_for_domain(domain, username, rid)
"""
import THREADS.sharedvariables as sharedvariables
from LOGGER.loggerconfig import logger


def found_domain_trust(trusting_domain_name, trusted_domain_name):
	"""
	Updates components when a domain trust is found.

	checks if the domains are already present in the databse,
	updates also their trust relationships
	"""
	global root_obj

	with sharedvariables.shared_lock:
		# check if the trusting domain exists in the root database
		trusting_domain = root_obj.get_or_create_domain(trusting_domain_name)

		# same domains trusting = trusted
		if trusting_domain_name == trusted_domain_name: 
			logger.debug(f"No need to add this trust: the domains are the same ({trusting_domain_name}) ({trusted_domain_name})")
			return

		# get or create the trusted domain
		trusted_domain = root_obj.get_or_create_domain(trusted_domain_name)

		# update the thrusts
		trusting_domain.add_domain_trust(trusted_domain)
		return 


def found_user_for_domain(domain, username, rid):
	"""
	UPdates components when a user is found for a domain 

	checks if the user is already placed in that domain.
	"""
	with sharedvariables.shared_lock:
		domainuser = domain.get_or_create_user_from_username(username)
		if rid is not None:
			domainuser.set_rid(rid)
		return 


def found_group_for_domain(domain, groupname, rid):
	"""
	Updates components when a group is found for a domain 

	checks if the group is already placed in that domain.
	domain, groupname: mandatory
	rid: non-mandatory
	"""
	with sharedvariables.shared_lock:
		domaingroup = domain.get_or_create_group_from_groupname(groupname)
		if rid is not None:
			domaingroup.set_rid(rid)
		return

