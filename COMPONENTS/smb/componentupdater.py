from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables

import COMPONENTS.hosts.componentupdater as hosts_componentupdater
import COMPONENTS.domains.componentupdater as domains_componentupdater


def associate_server_to_domain(domain, smb_server):
	"""
 	Associates the smb server to a domain.
  	"""
	# the server will have a reference to the domain
	smb_server.add_domain(domain)
 
	server_ip = smb_server.get_ip()
 
	# will add this ip to the list of smb servers
	domain.add_smb_server(server_ip)
	return 
	
	
def found_domain_name_for_smb_server(domain_name, smb_server):
	"""
	Found the domain of a SMB server.
	Update the domains list of machines for SMB.
	Add the domain association in the host and
	other services of the host 
	"""
	with sharedvariables.shared_lock:
		domain = sharedvariables.root_obj.get_or_create_domain(domain_name)
		host = smb_server.get_host()
		
		hosts_componentupdater.found_domain_for_host(host, domain)
		return 
	
	