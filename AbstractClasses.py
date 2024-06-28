
from abc import ABC, abstractmethod


class AbstractFilteredObject(ABC):
	@abstractmethod
	def captured(self):
		pass


class AbstractNetworkComponent(ABC):

    """
    method to display the network component, it should print what 
    this network component possesses. One level up, for example 
    when printing a network we should see it's port number so 
    the user can see them, just like the 'ls' command
    """
    @abstractmethod
    def get_context():
    	return dict()



class AbstractFilter(ABC): 
	"""
	The filter will return a list of the types of objects
	we find in the network -> the ones we're going to create
	in our database.
	"""
	@abstractmethod
	def filter() -> list: 
		pass



class AbstractMethod(ABC): 
	"""
	The main program will never depend on the exact methods
	of the command executioners. 
	"""
	@abstractmethod
	def run_method() -> None: 
		pass