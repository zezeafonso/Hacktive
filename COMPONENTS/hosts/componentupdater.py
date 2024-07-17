import THREADS.sharedvariables as sharedvariables


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