from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainGroupForUserThroughRPC(AbstractFilteredObject):
	def __init__(self, group_rid:str):
		self.group_rid = group_rid # hexadecimal

	def display(self):
		return f"found domain group with rid ({self.get_group_rid()}) for user"

	def get_group_rid(self):
		return self.group_rid

	def captured(self) -> dict:
		info = dict()
		info['group_rid'] = self.group_rid
		return info