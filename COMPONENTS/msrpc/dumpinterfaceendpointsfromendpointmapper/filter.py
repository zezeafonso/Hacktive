import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

class DumpInterfaceEndpointsFromEndpointMapper_Filter(AbstractFilter):
	_name = "filter dump interface endpoints from endpoint mapper"

	@staticmethod
	def filter(output:str) -> list:
		findings = []
		return findings