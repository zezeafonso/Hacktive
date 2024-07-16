import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from FILTEREDOBJECTS.network.foundnewipfornetwork import Filtered_NewIPForNetwork

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
			findings.append(Filtered_NewIPForNetwork([], ip))

		return findings