from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundMSRPCServiceIsUp(AbstractFilteredObject):
	def __init__(self, port:str):
		self.port = port

	def display(self):
		return f"Found MSRPC service was running on port ({self.port})"

	def get_port(self):
		return self.port

	def captured(self):
		return self.port