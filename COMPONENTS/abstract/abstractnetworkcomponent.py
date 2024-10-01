from abc import ABC, abstractmethod


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
 
	def auto_function_with_context(self, context):
		""" Common logic to be shared across subclasses """
		list_events = []
		for method in self.methods:
			list_events += method.create_run_events(context)
		return list_events