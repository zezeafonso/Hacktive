from LOGGER.loggerconfig import logger
import THREADS.sharedvariables as sharedvariables



def found_new_network_for_interface(interface_name, network_address):
	"""
	What we do when we receive a filtered_new_network_for_interface

	we get or create the interface.
	And for that interface we get or create the network.

	returns a dict with 'object' and 'methods' (if we created
	a new network or interface objects)
	"""

	with sharedvariables.shared_lock:
		logger.debug(f"network ({network_address}) for interface ({interface_name}) found -> updating components")
		
		interface = sharedvariables.root_obj.get_interface_or_create_it(interface_name)

		# ASKS THE USER IF HE WANTS THIS NETWORK
		network = interface.get_network_or_create_it(network_address)
		return 