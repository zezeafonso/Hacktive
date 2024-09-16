import re
import ipaddress

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfoundnewinterface import Filtered_FoundNewInterface
from COMPONENTS.filteredobjects.filteredfoundnewnetworkforinterface import Filtered_FoundNewNetworkForInterface
from COMPONENTS.filteredobjects.filteredfoundouripfornetwork import Filtered_FoundOurIPForNetwork



class ListInterfaces_Filter(AbstractFilter): 
	_filename = "outputs/ListInterfaces.out"
	_name = "list interfaces filter"

	"""
	Usar o stdout, do result, porque alguns comandos
	vao correr indeterminadamente e queremos analisar 
	a medida que vao saindo. Com ficheiros também dava,
	no entanto depois fica dificil porque teriamos de usar 
	locks. Quando estavamos a escrever e quando estavamos a ler.
	"""
	@staticmethod
	def filter(output:str) -> list: 
		"""
		objects that finds:
		+ FO.Filtered_NewNetworkForInterface(path=[current_interface], network=network_str)
		+ FO.Filtered_FoundOurIPForNetwork(path=[current_interface, network_str], ip=ip_str))
		+ FO.Filtered_NewInterface(path=[], interface=current_interface))
		"""
		findings = list() # the list of Filter objects we find

		# flags 
		interface_of_interest = False 
		current_interface = None
		current_interface_nc = None

		"""
		TODO: instead of creating the objects pass the objects
		"""

		for line in output.splitlines(): # IMPORTANT: because now they are outputs
			# if the line tells us the address (inet line)
			if line.strip().startswith('inet ') and interface_of_interest:

				# TODO: know the state of the interface 
				
				ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+/\d+)', line)
				if ip_match:
					ip_address = ip_match.group(1)

					# extract both IP address and network representation
					ip_str, network_prefix_length_str = ip_address.split('/')
					network = ipaddress.IPv4Network(ip_address, strict=False) 
					network_str = str(network)

					# FOUND NETWORK AND IP
					findings.append(Filtered_FoundNewNetworkForInterface(interface=current_interface, network=network_str))
					findings.append(Filtered_FoundOurIPForNetwork(interface=current_interface, network=network_str, ip=ip_str))

			# if we're reading a new interface
			elif re.match(r'^\d+:', line.strip()):
				# TODO: this works but I want to eliminate any loopback
				# and not just 'lo'
				current_interface = line.split(':')[1].strip()
				if current_interface != 'lo':
					interface_of_interest = True
					# interface found
					findings.append(Filtered_FoundNewInterface(path=[], interface=current_interface))
				else:
					interface_of_interest = False
		return findings