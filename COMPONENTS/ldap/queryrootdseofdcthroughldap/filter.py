import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from FILTEREDOBJECTS.ldap.founddomaincomponentsfromldapquery import Filtered_DomainComponentsFromLDAPQuery

class QueryRootDSEOfDCThroughLDAP_Filter(AbstractFilter):
	_name = "filter of querying the DC through Ldap to attain naming contexts"

	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		# Regular expression to match lines starting with 'namingcontexts:' and followed by 'DC='
		pattern = re.compile(r'defaultNamingContext:\s*((?:DC=([^,]+),?)+)')

		# Regular expression to capture the 'DC=' fields
		#dc_pattern = re.compile(r'DC=([^,]+)')
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				components = match.group(1).split(',')
				components = [component.split('=')[1] for component in components]
				filtered_obj = Filtered_DomainComponentsFromLDAPQuery({}, list_dc=components)
				findings.append(filtered_obj)
				
		return findings
		

