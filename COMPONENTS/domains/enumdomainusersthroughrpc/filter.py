import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomainuserthroughrpc import Filtered_FoundDomainUserThroughRPC

class EnumDomUsersThroughRPC_Filter(AbstractFilter):
	_name = "filter enum domain users through rpc"

	@staticmethod
	def filter(output:str) -> list:
		findings = list()
		# Define a regular expression pattern
		pattern = re.compile(r"user:\[([^\]]+)\] rid:\[([^\]]+)\]")

		# Iterate over each line and search for matches
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				user = match.group(1)
				rid_hex = match.group(2)
				rid_dec = int(rid_hex, 16)
				rid_str = str(rid_dec)

				findings.append(Filtered_FoundDomainUserThroughRPC(user, rid_str))
		return findings