from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables


def associate_server_to_domain(domain, smb_server):
	"""
 	Associates the smb server to a domain.
  	"""
	# the server will have a reference to the domain
	smb_server.associate_domain(domain)
 
	server_ip = smb_server.get_host().get_ip()
 
	# will add this ip to the list of smb servers
	domain.add_smb_server(server_ip)
	return 
	
	
	