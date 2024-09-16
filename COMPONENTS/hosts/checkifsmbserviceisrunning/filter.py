import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfoundsmbserviceisup import Filtered_FoundSMBServiceIsUp

class CheckIfSMBServiceIsRunning_Filter(AbstractFilter):
	_name = 'smb service scan filter'

	@staticmethod
	def filter(output:str) -> list:
		findings = []

		# output we're trying to parse
		# 445/tcp open  microsoft-ds

		# regular expression - ip group<type>
		pattern = re.compile(r'(\d+)\/(tcp|udp)\s+open\s+microsoft-ds')

		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				findings.append(Filtered_FoundSMBServiceIsUp(port=match.group(1)))
		
		return findings