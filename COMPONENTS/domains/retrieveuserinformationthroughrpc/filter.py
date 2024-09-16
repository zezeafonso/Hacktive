import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomainuserridthroughrpc import Filtered_FoundDomainUserRidThroughRPC

class RetrieveUserInformationThroughRPC_Filter(AbstractFilter):
	"""
	For now we are just parsing the RID from this output
	"""
	_name = "filter retrieve information from user through rpc"

	@staticmethod
	def filter(output:str) -> list:
		findings = list()
		# Define a regular expression pattern
		pattern = re.compile(r"user_rid:\s+(0x[0-9a-fA-F]+)")

		# Iterate over each line and search for matches
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				rid_hex = match.group(1)
				rid_hex_str = str(rid_hex)

				findings.append(Filtered_FoundDomainUserRidThroughRPC(rid_hex_str))
		return findings