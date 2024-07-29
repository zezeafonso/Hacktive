import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter


class BasicCrackMapExec_Filter(AbstractFilter):
	_name = "filter basic crackmapexec"

	@staticmethod
	def filter(output:str) -> list:
		return []