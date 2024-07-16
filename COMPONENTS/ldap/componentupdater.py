from THREADS.sharedvariables import shared_lock
from THREADS.sharedvariables import root_obj


def found_new_domain_components_path_ldap(host, domain_components_path):
	"""
	Updates the network components for the event of finding new 
	domain components path through ldap. 
	We found a ldap server and we might have found a Domain Controller's domain name.

	+ we received a filtered object from the filter it means that the 
	service is on. Which means this host (if it doesn't have already) 
	must have an ldap service associated. 
	+ gets/creates the ldap server for the host
	+ associates the domain to the host
	+ add's this host as a DC to the domain

	Next we must check if any of the names corresponds to a domain name
	"""
	with shared_lock:
		# create or get the ldap server role for this host
		ldap_server = host.get_or_add_role_ldap_server()

		# check if the domain exists in the root database
		domain = root_obj.get_or_create_domain(domain_components_path)
		
		# there is only 1 domain for each host
		# put the host as a dependent object of the domain.
		host.associate_domain_to_host_if_not_already(domain) 

		# put this host as a DC for the domain
		domain.add_dc(ldap_server)
	return