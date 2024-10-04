

def associate_server_to_domain(domain, dns_server):
	"""
 	Associates the smb server to a domain.
  	"""
	# the server will have a reference to the domain
	dns_server.add_domain(domain)
 
	server_ip = dns_server.get_ip()
 
	# will add this ip to the list of smb servers
	domain.add_dns_server(server_ip)
	return 