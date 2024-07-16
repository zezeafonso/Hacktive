import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfoundnetbioshostnameforip import Filtered_FoundNetBIOSHostnameForIP
from COMPONENTS.filteredobjects.filteredfoundnetbiosgroupforip import Filtered_FoundNetBIOSGroupForIP
from COMPONENTS.filteredobjects.filteredfoundpdcipfornetbiosgroup import Filtered_FoundPDCIPForNetBIOSGroup
from COMPONENTS.filteredobjects.filteredfoundnetbioshostnamewithsmb import Filtered_FoundNetBIOSHostnameWithSMB

			
class NBNSIPTranslation_Filter(AbstractFilter):
	_name = "translation of ip to hostname through NBNS FILTER"

	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		pattern_00 = re.compile(r'^\s*(\S+)\s+<00>\s+-\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		pattern_group = re.compile(r'^\s*(\S+)\s+<(00|1c)>\s+-\s+<GROUP>\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		pattern_20 = re.compile(r'^\s*(\S+)\s+<20>\s+-\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		pattern_1b = re.compile(r'^\s*(\S+)\s+<1b>\s+-\s+[BMH]\s+<ACTIVE>\s*$', re.MULTILINE)
		
		ip_pattern = re.compile(r'Looking up status of (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

		# Find matches
		matches_00 = pattern_00.findall(output)
		matches_group = pattern_group.findall(output)
		matches_20 = pattern_20.findall(output)
		matches_1b = pattern_1b.findall(output)
		match_ip = ip_pattern.search(output)

		if match_ip:
			ip_address = match_ip.group(1)

		for match in matches_00: # will just be one but yes
			findings.append(Filtered_FoundNetBIOSHostnameForIP({}, hostname=match, ip=ip_address))

		for match in matches_group:
			group = match[0]
			_type = match[1]
			findings.append(Filtered_FoundNetBIOSGroupForIP({}, group, _type, ip=ip_address))

		for match in matches_20:
			findings.append(Filtered_FoundNetBIOSHostnameWithSMB({}, hostname=match, ip=ip_address))

		for match in matches_1b:
			findings.append(Filtered_FoundPDCIPForNetBIOSGroup({}, group=match, ip=ip_address))

		return findings
