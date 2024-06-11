import re
import ipaddress

import NetworkComponents as NC
from AbstractClasses import AbstractNetworkComponent
from AbstractClasses import AbstractFilter
import FilterObjects as FO

global interface_dictionary
global network_dictionary
global livehost_dictionary

services = ['domain', 'kerberos-sec', 'msrpc', 'ldap', 'microsoft-ds']

"""
This serves to know if the Network Components we'll create 
in outputs_listener already exist. 

If it exists that we return that object, since we want to add 
new things to it, or update it's state.

For these operations I don't think you need a lock, because 
in each point in time there will only be one filter working.

LOCK: if we change this behaviour to filter with threads/processes
"""
def init_dictionaries():
	global interface_dictionary 
	global network_dictionary
	global livehost_dictionary

	interface_dictionary = {}
	network_dictionary = {}
	livehost_dictionary = {}
	pass



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
					findings.append(FO.Filtered_NewNetworkForInterface(interface=current_interface, network=network_str))
					findings.append(FO.Filtered_FoundOurIPForNetwork(interface=current_interface, network=network_str, ip=ip_str))

			# if we're reading a new interface
			elif re.match(r'^\d+:', line.strip()):
				# TODO: this works but I want to eliminate any loopback
				# and not just 'lo'
				current_interface = line.split(':')[1].strip()
				if current_interface != 'lo':
					interface_of_interest = True
					# interface found
					findings.append(FO.Filtered_NewInterface(path=[], interface=current_interface))
				else:
					interface_of_interest = False
		return findings



class PortScan_Filter(AbstractFilter):
	_name = 'port scan filter'

	@staticmethod
	def filter(output:str) -> list: 
		# define the list of objects to attach to the nc that called this filter
		list_objects = list()
		# define the list of auto methods to call after these new NC's are attached
		auto_methods = list()
		# define the regular expression to catch open ports
		port_service_re = re.compile(r"(\d+)/tcp\s+open\s+(\S+)")

		# Parse the lines to extract port numbers
		for line in output.splitlines():
			match = port_service_re.search(line)
			if match:
				port, service = match.groups()
				if service in services: # global variable DICT
					NC.Port(port, service)
					# throw the port to the done thread
					# put the checks in the other side and not here
					print(service)
		return [], []




class ArpScan_Filter(AbstractFilter):
	_name = "arp scan filter"

	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		pattern = r'Nmap scan report for ([\d.]+)\nHost is up'
		# Find all matches in the Nmap output
		alive_hosts = re.findall(pattern, output)

		for ip in alive_hosts:
			# found ip for the network, we don't know the network
			findings.append(FO.Filtered_NewIPForNetwork([], ip))

		return findings


		    
class NBNSIPTranslation_Filter(AbstractFilter):
	_name = "translation of ip to hostname through NBNS FILTER"

	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		pattern_00 = re.compile(r'^\s*(\S+)\s+<00>\s+-\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		pattern_group_00 = re.compile(r'^\s*(\S+)\s+<00>\s+-\s+<GROUP>\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		pattern_20 = re.compile(r'^\s*(\S+)\s+<20>\s+-\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		pattern_1b = re.compile(r'^\s*(\S+)\s+<1b>\s+-\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		
		ip_pattern = re.compile(r'Looking up status of (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

		# Find matches
		matches_00 = pattern_00.findall(output)
		matches_group_00 = pattern_group_00.findall(output)
		matches_20 = pattern_20.findall(output)
		matches_1b = pattern_1b.findall(output)
		match_ip = ip_pattern.search(output)

		if match_ip:
			ip_address = match_ip.group(1)

		for match in matches_00: # will just be one but yes
			findings.append(FO.Filtered_FoundNetBIOSHostnameForIP({}, hostname=match, ip=ip_address))

		for match in matches_group_00:
			findings.append(FO.Filtered_FoundNetBIOSGroupForIP({}, group=match, ip=ip_address))

		for match in matches_20:
			findings.append(FO.Filtered_FoundNetBIOSHostnameWithSMB({}, hostname=match))

		for match in matches_1b:
			findings.append(FO.Filtered_FoundPDCIPForNetBIOSGroup({}, group=match, ip=ip_address))

		print(f"findings: {findings}")
		return findings


class QueryNamingContextOfDCThroughLDAP_Filter(AbstractFilter):
	_name = "filter of querying the DC through Ldap to attain naming contexts"

	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		# Regular expression to match lines starting with 'namingcontexts:' and followed by 'DC='
		pattern = re.compile(r'^namingcontexts:\s+DC=[^,]*')

		# Regular expression to capture the 'DC=' fields
		dc_pattern = re.compile(r'DC=([^,]+)')

		# Parse the lines to extract port numbers
		for line in output.splitlines():
			if pattern.match(line):
				# Find all 'DC=' fields in the line
				dcs = dc_pattern.findall(line)

				# create the filtered object for every pattern of this type
				# ex: foxriver.local; forestDNSZones.foxriver.local ...
				findings.append(FO.Filtered_DomainComponentsFromLDAPQuery({}, list_dc=dcs))
		
		return findings


class ResponderAnalyzeInterface_Filter(AbstractFilter):
	pass