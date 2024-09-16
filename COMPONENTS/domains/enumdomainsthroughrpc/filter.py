import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

class EnumDomainsThroughRPC_Filter(AbstractFilter):
	_name = "filter enumdomains through rpc"

	@staticmethod
	def filter(output:str) -> list:
		findings = []
		return findings
