import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

class RetrieveListUsersWithWindapsearch_Filter(AbstractFilter):
	_name = "Filter list of users with windapsearch"
	
	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []
		return findings