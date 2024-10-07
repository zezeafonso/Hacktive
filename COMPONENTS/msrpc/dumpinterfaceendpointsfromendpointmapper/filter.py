import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfoundmsparininterfaces import Filtered_FoundMSPARInInterfaces

class DumpInterfaceEndpointsFromEndpointMapper_Filter(AbstractFilter):
	_name = "filter dump interface endpoints from endpoint mapper"

	@staticmethod
	def filter(output:str) -> list:
		findings = []

		# Regular expression to match lines starting with 'namingcontexts:' and followed by 'DC='
		ms_par_pattern = re.compile(r'ms-par')

		# Regular expression to capture the 'DC=' fields
		for line in output.splitlines():
			ms_par_match = ms_par_pattern.search(line, re.IGNORECASE)
			# default naming context = domain name without the DC=...
			if ms_par_match:
				filtered_obj = Filtered_FoundMSPARInInterfaces()
				findings.append(filtered_obj)
		return findings