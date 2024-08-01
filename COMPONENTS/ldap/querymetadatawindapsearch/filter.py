import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfounddefaultnamingcontext import Filtered_founddefaultnamingcontext
from COMPONENTS.filteredobjects.filteredfounddnshostname import Filtered_founddnshostname



class QueryMetadataWindapsearch_Filter(AbstractFilter):
	_name = "filter of querying metadata of LDAP through windapsearch"

	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []
		dns_hostname_pattern = re.compile(r'dnsHostName:\s+(?P<dnsHostName>[^\s]+)')
		default_naming_context_pattern = re.compile(r'defaultNamingContext:\s+(?P<defaultNamingContext>[^\s]+)')

		dns_hostname_match = dns_hostname_pattern.search(output)
		default_naming_context_match = default_naming_context_pattern.search(output)

		if dns_hostname_match:
			dns_hostname = dns_hostname_match.group('dnsHostName')
			fo = Filtered_founddnshostname(dns_hostname=dns_hostname)
			findings.append(fo)
			

		if default_naming_context_match:
			default_naming_context = default_naming_context_match.group('defaultNamingContext')
			# Strip the DC= parts and join the remaining parts with dots
			stripped_naming_context = '.'.join(part.split('=')[1] for part in default_naming_context.split(','))
			# create the filtered object
			fo = Filtered_founddefaultnamingcontext(naming_context=stripped_naming_context)
			findings.append(fo)

		return findings