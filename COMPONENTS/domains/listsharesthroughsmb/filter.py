import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter


class ListSharesThroughSMB_Filter(AbstractFilter):
	_name = "filter list sharers through SMB"

	@staticmethod
	def filter(output:str) -> list:
		return []