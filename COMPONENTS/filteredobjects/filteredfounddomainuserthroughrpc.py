from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject


class Filtered_FoundDomainUserThroughRPC(AbstractFilteredObject):
	def __init__(self, user:str, rid:str):
		self.user = user
		self.rid = rid

	def display(self):
		return f"Found Domain User through rpc ({self.user}) with rid: ({self.rid})"

	def get_user(self):
		return self.user 

	def get_rid(self):
		return self.rid

	def captured(self):
		return 