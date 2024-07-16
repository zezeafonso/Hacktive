import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfoundmsrpcserviceisup import Filtered_FoundMSRPCServiceIsUp

class CheckIfMSRPCServiceIsRunning_Filter(AbstractFilter):
	_name = 'msrpc service scan filter' 

	@staticmethod 
	def filter(output:str) -> list:
		findings = []

		# output we're trying to parse
		# 135/tcp open ms-rpc

		pattern = re.compile(r'(\d+)\/(tcp|udp)\s+open\s+msrpc')
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				findings.append(Filtered_FoundMSRPCServiceIsUp(port=match.group(1)))

		return findings