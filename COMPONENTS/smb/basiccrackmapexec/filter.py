import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

# create for SMB signing 
# create for SMBv1 enabled or not
from COMPONENTS.filteredobjects.filteredfoundsmbservicesigning import Filtered_FoundSMBServiceSigning
from COMPONENTS.filteredobjects.filteredfoundsmbv1value import Filtered_FoundSMBv1Value
from COMPONENTS.filteredobjects.filteredfounddomainofmachine import Filtered_FoundDomainOfMachine

class BasicCrackMapExec_Filter(AbstractFilter):
	_name = "filter basic crackmapexec"

	@staticmethod
	def filter(output:str) -> list:
		findings = list()
		# Regular expression pattern to match and extract the required fields, ignoring ANSI escape codes
		pattern = re.compile(
			r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
			r"(?P<port>\d+)\s+"
			r"(?P<hostname>\S+)\s+\033\[.*?\[\*\]\033\[.*?m\s+"
			r"(?P<os>Windows\s+[\d\.]+)\s+Build\s+(?P<build>\d+)\s+(?P<arch>x64|x86)\s+"
			r"\(name:(?P<name>[^)]+)\)\s+"
			r"\(domain:(?P<domain>[^)]+)\)\s+"
			r"\(signing:(?P<signing>True|False)\)\s+"
			r"\(SMBv1:(?P<smbv1>True|False)\)"
		)

		match = pattern.search(output)
		if match:
			#ip = match.group('ip') # not needed 
			#port = match.group('port') 
			#hostname = match.group('hostname') 
			#os = match.group('os') # not needed
			#build = match.group('build') # not needed
			#name = match.group('name') 
			domain = match.group('domain') 
			signing = match.group('signing') 
			smbv1 = match.group('smbv1') 
   
			findings.append(Filtered_FoundSMBServiceSigning(signing))
			findings.append(Filtered_FoundSMBv1Value(smbv1))
			findings.append(Filtered_FoundDomainOfMachine(domain))

		return findings