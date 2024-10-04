import THREADS.sharedvariables as sharedvariables
from LOGGER.loggerconfig import logger

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

def update_components_found_dns_service_is_running(host, port):
	"""
 	Updates the components when we find that a DNS service is running 
	for a host
 	"""
	with sharedvariables.shared_lock:
		# TODO: implement this function
		dns_server = host.found_dns_service_running_on_port(port)
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

		# if already is dc for this domain 
		if host.check_if_host_is_dc_for_domain(domain):
			return 

		# check for different domains
		if host.check_if_host_has_domain():
			# different domains
			if id(host.get_domain) != id(domain):
				logger.debug(f"Found that host ({host.get_ip()}) is DC for different domain\
        			previous ({host.get_domain().get_domain_name()}) \
               		present ({domain.get_domain_name()})")
				return 
		
		# the host will know his domain
		host.add_domain(domain)

		# the services will know the domain
		host.associate_host_services_to_domain(domain)
		
		# domain will know this host as DC
		domains_componentupdater.found_dc_for_domain(domain, host)
	return


def found_dns_hostname_for_host(host, dns_hostname):
	"""
	Updates the host components when we find a dns hostname
	"""
	with sharedvariables.shared_lock:
		host.add_dns_hostname(dns_hostname)
		return