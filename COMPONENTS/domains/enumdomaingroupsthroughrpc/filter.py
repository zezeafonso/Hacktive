import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomaingroupthroughrpc import Filtered_FoundDomainGroupThroughRPC



class EnumDomGroupsThroughRPC_Filter(AbstractFilter):
	_name = "filter enum domain groups through rpc"

	@staticmethod
	def filter(output:str) -> list:
		findings = list()
		# Define a regular expression pattern
		pattern = re.compile(r"group:\[([^\]]+)\] rid:\[([^\]]+)\]")

		# Iterate over each line and search for matches
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				group = match.group(1)
				rid_hex = match.group(2)
				rid_hex_str = str(rid_hex)
				rid_dec = int(rid_hex, 16)
				rid_str = str(rid_dec)

				findings.append(Filtered_FoundDomainGroupThroughRPC(group, rid_hex_str))
		return findings