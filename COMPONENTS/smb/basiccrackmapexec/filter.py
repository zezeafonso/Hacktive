import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

# create for SMB signing 
# create for SMBv1 enabled or not
from COMPONENTS.filteredobjects.filteredfoundsmbservicesigning import Filtered_FoundSMBServiceSigning
from COMPONENTS.filteredobjects.filteredfoundsmbv1value import Filtered_FoundSMBv1Value
from COMPONENTS.filteredobjects.filteredfounddomainofmachine import Filtered_FoundDomainOfMachine
from COMPONENTS.filteredobjects.filteredfoundsmbserverversion import Filtered_FoundSMBServerVersion

class BasicCrackMapExec_Filter(AbstractFilter):
	_name = "filter basic crackmapexec"

	@staticmethod 
	def filter(output:str) -> list:
		# list of filtered objects
		list_fo = list()
		
  		# Regex to match the server version and fields inside parentheses
		version_pattern = re.search(r'\[\*\]\s+(.+?)\s+\(', output)
		fields_pattern = re.findall(r'\(([^:]+):([^)]+)\)', output)

		# Extract server version
		server_version = version_pattern.group(1).strip() if version_pattern else None

		# Extract valuable fields
		fields = {field[0].strip(): field[1].strip() for field in fields_pattern}
		for field in fields: 
			# hostname
			if field == 'name':
				list_fo.append(Filtered_FoundSMBServerVersion(fields[field]))
			if field == 'domain':
				list_fo.append(Filtered_FoundDomainOfMachine(fields[field]))
			if field == 'signing':
				list_fo.append(Filtered_FoundSMBServiceSigning(fields[field]))
			if field == 'SMBv1':
				list_fo.append(Filtered_FoundSMBv1Value(fields[field]))

		return list_fo
