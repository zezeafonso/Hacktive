import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from FILTEREDOBJECTS.netbios.foundnetbiosgroupforip import Filtered_FoundNetBIOSGroupForIP

class NBNSGroupMembers_Filter(AbstractFilter):
	_name = "netbios group membership filter"

	@staticmethod
	def filter(output:str) -> list:
		findings = []

		# regular expression - ip group<type>
		pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+)\s+(\w+)<(00|1c)>')

		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				findings.append(Filtered_FoundNetBIOSGroupForIP({}, match.group(2), match.group(3), match.group(1)))
		
		return findings