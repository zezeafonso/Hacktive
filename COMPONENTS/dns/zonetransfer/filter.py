import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

class ZoneTransfer_Filter(AbstractFilter):
	"""
	For now just run it
	"""
	_name = "DNS zone transfer"

	@staticmethod
	def filter(output:str) -> list: 
		return []