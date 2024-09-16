from abc import ABC, abstractmethod

class AbstractFilter(ABC): 
	"""
	The filter will return a list of the types of objects
	we find in the network -> the ones we're going to create
	in our database.
	"""
	@abstractmethod
	def filter() -> list: 
		pass
