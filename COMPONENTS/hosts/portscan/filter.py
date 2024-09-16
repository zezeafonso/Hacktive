import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter


class PortScan_Filter(AbstractFilter):
	_name = 'port scan filter'

	@staticmethod
	def filter(output:str) -> list: 
        # TODO: implement the filter
		return []