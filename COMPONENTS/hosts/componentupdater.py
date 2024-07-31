import THREADS.sharedvariables as sharedvariables

import COMPONENTS.domains.componentupdater as domains_componentupdater

def update_components_found_msrpc_service_is_running(host, port):
	"""
	Updates the components when we find that a msrpc service is running 
	for a host
	"""
	with sharedvariables.shared_lock:
		msrpc_server = host.found_msrpc_service_running_on_port(port)
		return

def update_components_found_smb_service_is_running(host, port):
	"""
	Updates the components when we find that an smb service is running
	for a host
	"""
	with sharedvariables.shared_lock:
		smb_server = host.found_smb_service_running_on_port(port)
		return


def found_domain_for_host(host, domain):
	"""
 	Associated the domain for a host.
  	Also calls function to associate the host in the domain
   	"""
	with sharedvariables.shared_lock:
		# already has a domain
		if host.check_if_host_has_domain():
			return 

		# the host will know his domain
		host.add_domain(domain)

		# the services will know the domain
		host.associate_host_services_to_domain(domain)
	
		# call the function that associates the host to the domain
		domains_componentupdater.found_host_for_domain(domain, host)
	return 


def found_domain_for_dc_host(host, domain):
	"""
	Associates a domain to the host.
	The host in this case will be a Domain Controller for the domain
	It might already know that is part of the domain.
	"""
	with sharedvariables.shared_lock:
  		# checks if host already has the DC services (SMB; LDAP; RPC)
		# creates them if it doesn't
		host.add_dc_services() 
  
		# the host will know his domain
		host.add_domain(domain)

		# the services will know the domain
		host.associate_host_services_to_domain(domain)
		
		# associate the domain in host, and in its services
		#host.associate_domain_to_host_if_not_already(domain) 
		
		# put this host as a DC for the domain
		# TODO: call the correct function from the domain componentupdater
		#domain.add_dc(host)
		# call the function that associates the host to the domain
		domains_componentupdater.found_dc_for_domain(domain, host)
	return