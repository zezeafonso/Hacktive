import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfoundLDAPServiceIsUp import Filtered_FoundLDAPServiceIsUp

class CheckIfLDAPServiceIsRunning_Filter(AbstractFilter):
	_name = 'ldap service scan filter' 

	@staticmethod 
	def filter(output:str) -> list:
		findings = []

		# output we're trying to parse
		# 636/tcp open ldapssl

		pattern = re.compile(r'(\d+)\/(tcp|udp)\s+open\s+ldapssl')
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				findings.append(Filtered_FoundLDAPServiceIsUp(port=match.group(1)))

		return findings