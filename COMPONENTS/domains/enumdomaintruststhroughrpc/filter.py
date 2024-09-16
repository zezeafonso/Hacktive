import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomaintrust import Filtered_FoundDomainTrust

class EnumDomainTrustsThroughRPC_Filter(AbstractFilter):
	_name = "filter enum domain trusts through rpc"

	@staticmethod
	def filter(output:str) -> list:
		findings = []
		pattern_number = re.compile(r'[0-9]+\s+domains\s+returned')
		for line in output.splitlines():
			match = pattern_number.search(line)
			if match:
				pass # nothing to be done
			else:

				domain_name = line.split(' ')[0] # domain name split by space
				filtered_obj = Filtered_FoundDomainTrust(domain_name=domain_name)
				findings.append(filtered_obj)

		return findings