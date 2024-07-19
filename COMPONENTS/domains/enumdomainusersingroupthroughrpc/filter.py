import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomainuserforgroupthroughrpc import Filtered_FoundDomainUserForGroupThroughRPC

class EnumDomUsersThroughRPC_Filter(AbstractFilter):
	_name = "filter enum domain users through rpc"

	@staticmethod
	def filter(output:str) -> list:
		findings = list()
		# Define a regular expression pattern
		pattern = re.compile(r"rid:\[([^\]]+)\] attr:\[([^\]]+)\]")

		# Iterate over each line and search for matches
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				rid_hex = match.group(1)
				attr = match.group(2) # CHECK THIS OUTPUT AND IF ITS RELEVANT
				rid_hex_str = str(rid_hex)

				findings.append(Filtered_FoundDomainUserForGroupThroughRPC(rid_hex_str))
		return findings