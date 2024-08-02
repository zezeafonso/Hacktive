import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfounddomaincomponentsfromldapquery import Filtered_FoundDomainComponentsFromLDAPQuery
from COMPONENTS.filteredobjects.filteredfounddnshostname import Filtered_founddnshostname

class QueryRootDSEOfDCThroughLDAP_Filter(AbstractFilter):
	_name = "filter of querying the DC through Ldap to attain naming contexts"

	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		# Regular expression to match lines starting with 'namingcontexts:' and followed by 'DC='
		def_naming_context_pattern = re.compile(r'defaultNamingContext:\s*((?:DC=([^,]+),?)+)')
		# Regular expression to match lines starting with 'dnsHostName:'
		dns_hostname_pattern = re.compile(r'dnsHostName:\s*([\w.-]+)')

		# Regular expression to capture the 'DC=' fields
		#dc_pattern = re.compile(r'DC=([^,]+)')
		for line in output.splitlines():
			match = def_naming_context_pattern.search(line)
			dns_hostname_match = dns_hostname_pattern.search(line)
			if match:
				components = match.group(1).split(',')
				components = [component.split('=')[1] for component in components]
				filtered_obj = Filtered_FoundDomainComponentsFromLDAPQuery({}, list_dc=components)
				findings.append(filtered_obj)
			if dns_hostname_match:
				dns_hostname = dns_hostname_match.group(1)
				filtered_obj = Filtered_founddnshostname(dns_hostname)
				findings.append(filtered_obj)
				
		return findings
		

