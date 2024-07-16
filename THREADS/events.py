from AbstractClasses import AbstractNetworkComponent
from AbstractClasses import AbstractFilter
from AbstractClasses import AbstractMethod

#########################
# Class EVENT
"""
The event classes describe the event that we want 
to pass from thread to thread. There are two types:
+ run event: to run a new command
+ done event: when the command as run 

With this in mind there will be two specific threads
one to listen to run_events and another to listen for
done_events.
"""
class Event:
	def __init__(self, type:str):
		self.type = type



class Run_Event(Event):
	"""
	Intended for the runcommandsthread.
	"""
	def __init__(self, type:str, filename:str, command:str, method:AbstractMethod, nc:AbstractNetworkComponent, context:dict):
		super().__init__(type)
		self.out_file = filename
		self.command = command
		self.method = method
		self.context = context

	def get_attributes(self):
		return self.out_file, self.command, self.method, self.context
	



class Done_Event(Event):
	"""
 	Inteded for the parseoutputs thread
  	"""
	def __init__(self, type:str, command:str, output:str, return_code:int, method:AbstractMethod, nc:AbstractNetworkComponent, context:dict):
		super().__init__(type)
		self.command = command
		self.output = output
		self.return_code = return_code
		self.method = method
		self.context = context

	def get_attributes(self):
		return self.command, self.output, self.return_code, self.method, self.context

