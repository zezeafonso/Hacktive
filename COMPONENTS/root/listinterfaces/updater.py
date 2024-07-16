from THREADS.sharedvariables import root_obj
from COMPONENTS.root.componentupdater import found_new_interface
from COMPONENTS.network.componentupdater import found_our_ip_for_a_network
from COMPONENTS.interface.componentupdater import found_new_network_for_interface

from COMPONENTS.filteredobjects.filteredfoundnewnetworkforinterface import Filtered_FoundNewNetworkForInterface
from COMPONENTS.filteredobjects.filteredfoundouripfornetwork import Filtered_FoundOurIPForNetwork
from COMPONENTS.filteredobjects.filteredfoundnewinterface import Filtered_FoundNewInterface

def update_list_interfaces(context:dict, filtered_objects:list):
	"""
	Defines the components we update when we list the interfaces available
	"""
	global root_obj

	for filtered_obj in filtered_objects:
		# FOUND NEW INTERFACE
		if isinstance(filtered_obj, Filtered_FoundNewInterface):
			interface_name = filtered_obj.get_interface_name()
			found_new_interface(interface_name)
			

		# FOUND NEW NETWORK FOR AN INTERFACE
		elif isinstance(filtered_obj, Filtered_FoundNewNetworkForInterface):
			interface_name = filtered_obj.get_interface_name()
			network_address = filtered_obj.get_network_address()
			found_new_network_for_interface(interface_name, network_address)

		# FOUND OUR IP
		elif isinstance(filtered_obj, Filtered_FoundOurIPForNetwork):
			interface_name = filtered_obj.get_interface_name()
			network_address = filtered_obj.get_network_address()
			ip = filtered_obj.get_ip()
			found_our_ip_for_a_network(interface_name, network_address, ip)
	return 