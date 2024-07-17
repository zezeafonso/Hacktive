import THREADS.sharedvariables as sharedvariables

from LOGGER.loggerconfig import logger


def found_new_interface(interface_name):
	"""
	What we do when filter found a Filtered object
	of type filtered_newinterface

	returns dict 'object' and 'methods' (if a new
	interface network component was created)
	"""
	
	with sharedvariables.shared_lock:
		logger.debug(f"interface: ({interface_name}) found -> updating components")
		
		interface = sharedvariables.root_obj.get_interface_or_create_it(interface_name) # already calls the methods
		return 





