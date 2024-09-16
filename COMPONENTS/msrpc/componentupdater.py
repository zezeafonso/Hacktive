from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables


def associate_server_to_domain(domain, rpc_server):
	"""
 	Associates the smb server to a domain.
  	"""
	# the server will have a reference to the domain
	rpc_server.add_domain(domain)
 
	server_ip = rpc_server.get_ip()
 
	# will add this ip to the list of smb servers
	domain.add_msrpc_server(server_ip)
	return 