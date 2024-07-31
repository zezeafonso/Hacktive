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


def found_user_rid_belonging_to_group_rid(domain, group_rid, user_rid):
	"""
	Updates components when we find a user rid that belongs to 
	a group (identified by it's rid) for a specific domain 
	(identified by its domain name)
	"""
	with sharedvariables.shared_lock:
		domaingroup = domain.get_or_create_group_from_rid(group_rid)
		if user_rid is not None:
			# get the user from it's rid or create it
			domainuser = domain.get_or_create_user_from_rid(user_rid)
			# add the user the group 
			domaingroup.add_user(domainuser)
			# add the group to the user
			domainuser.add_group(domaingroup)
			
		return


def found_group_rid_for_user_rid(domain, user_rid, group_rid):
	"""
	Updates components when we find a group rid for a user rid.
	Meaning we found a new group that the user belongs to.
	The group and user (both identified by their rid) belonging
	to a specific domain (identified by its domain name)
	"""
	with sharedvariables.shared_lock:
		domainuser = domain.get_or_create_user_from_rid(user_rid)
		if group_rid is not None:
			# get the group from it's rid or create it 
			domaingroup = domain.get_or_create_group_from_rid(group_rid)
			# add the group to the user
			domainuser.add_group(domaingroup)
			# add the user to the group
			domaingroup.add_user(domainuser)
			

def found_user_rid_for_username(domain, username, user_rid):
	"""
 	Updates components when we find a user_rid for a username 
  	that belongs to a domain
   	"""
	with sharedvariables.shared_lock:
		# get the username
		domainuser = domain.get_or_create_user_from_username(username)
		if user_rid is not None:
			domainuser.set_rid(user_rid)
			return 


def found_dc_for_domain(domain, host):
	"""
	Found a DC for a domain. 
	Add the host to the list of DCs.
	Add interesting servers from host to our list of servers
	"""
	with sharedvariables.shared_lock:
		# add the host to dc list
		domain.add_dc(host)
		# add the dc services to the domain
		domain.add_dc_services(host)
		return 


def found_host_for_domain(domain, host):
	"""
 	We found a host for a domain.
  	Add the host to list of machines.
   	Add interesting servers from host to our list of servers
	"""
	with sharedvariables.shared_lock:
		# add the host to domains machine list
		domain.add_host(host)
		# add the host services to the domain
		domain.add_host_services(host)
		return 
		