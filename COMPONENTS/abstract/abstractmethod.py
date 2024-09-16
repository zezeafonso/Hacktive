from abc import ABC, abstractmethod

class AbstractMethod(ABC): 
	"""
	The main program will never depend on the exact methods
	of the command executioners. 
	"""
	@abstractmethod
	def run_method() -> None: 
		pass