import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfounddnsserviceisup import Filtered_FoundDNSServiceIsUp

class CheckIfDNSServiceIsRunning_Filter(AbstractFilter):
	_name = 'dns service scan filter' 

	@staticmethod 
	def filter(output:str) -> list:
		findings = []

		# output we're trying to parse
		# 23/tcp open domain

		pattern = re.compile(r'(\d+)\/(tcp|udp)\s+open\s+domain')
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				findings.append(Filtered_FoundDNSServiceIsUp(port=match.group(1)))

		return findings