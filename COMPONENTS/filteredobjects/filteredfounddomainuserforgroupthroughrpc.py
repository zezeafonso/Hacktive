from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainUserForGroupThroughRPC(AbstractFilteredObject):
	def __init__(self, user_rid:str):
		self.user_rid = user_rid # in hexadecimal for now

	def display(self):
		return f"domain user with rid ({self.user_rid}) found in group"

	def get_user_rid(self):
		# returns in hexadecimal
		return self.user_rid

	def captured(self) -> dict:
		d = dict()
		d['user_rid'] = self.get_user_rid()
		return d