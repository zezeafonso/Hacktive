import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomainsid import Filtered_FoundDomainSID

class RetrieveDomainSIDThroughRPC_Filter(AbstractFilter):
	_name = "filter enum domain users through rpc"

	@staticmethod
	def filter(output:str) -> list:
		findings = list()
		# Define a regular expression pattern
		# Regular expression pattern to capture the Domain SID
		pattern = r"Domain Sid:\s+([A-Za-z0-9\-]+)"

		# Using re.search to find the SID in the output
		match = re.search(pattern, output)

		if match:
			domain_sid = match.group(1)
			
			findings.append(Filtered_FoundDomainSID(domain_sid))
		return findings