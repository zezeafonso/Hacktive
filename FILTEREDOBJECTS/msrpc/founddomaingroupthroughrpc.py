from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_DomainGroupThroughRPC(AbstractFilteredObject):
	def __init__(self, group:str, rid:str):
		self.group = group
		self.rid = rid 

	def display(self):
		return f"Found Domain Group through rpc ({self.group}) with rid: ({self.rid})"

	def get_group(self):
		return self.group

	def get_rid(self):
		return self.rid 

	def captured(self):
		return 