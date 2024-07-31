import THREADS.sharedvariables as sharedvariables



def found_new_domain_components_path_ldap(host, domain_components_path):
	"""
	Updates the network components for the event of finding new 
	domain components path of a domain through ldap. 
	We found a ldap server. 

	+ we received a filtered object from the filter it means that the 
	service is on. Which means this host (if it doesn't have already) 
	must have an ldap service associated. 
	+ gets/creates the ldap server for the host
	+ associates the domain to the host
	+ add's this host as a DC to the domain

	Next we must check if any of the names corresponds to a domain name
	"""
	with sharedvariables.shared_lock:
		# create or get the ldap server role for this host
		ldap_server = host.get_or_add_role_ldap_server()

		# check if the domain exists in the root database
		domain = sharedvariables.root_obj.get_or_create_domain(domain_components_path)
  
  		# checks if host already has the DC services (SMB; LDAP; RPC)
		# creates them if it doesn't
		host.add_dc_services() 
		
		# associate the domain in host, and in its services
		host.associate_domain_to_host_if_not_already(domain) 

		# put this host as a DC for the domain
		domain.add_dc(host)
	return


def associate_server_to_domain(self, domain, ldap_server):
	"""
 	Associates the smb server to a domain.
  	"""
	# the server will have a reference to the domain
	ldap_server.add_domain(domain)
 
	server_ip = ldap_server.get_host().get_ip()
 
	# will add this ip to the list of smb servers
	domain.add_ldap_server(server_ip)
	return 