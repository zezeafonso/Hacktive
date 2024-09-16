import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter


class SpiderSharesThroughSMB_Filter(AbstractFilter):
	_name = "filter spider shares through SMB"

	@staticmethod
	def filter(output:str) -> list:
		return []