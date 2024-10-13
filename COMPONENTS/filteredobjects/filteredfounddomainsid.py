from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainSID(AbstractFilteredObject):
	def __init__(self, sid:str):
		self.sid = sid # True|False

	def display(self):
		return f"Found domain SID ({self.sid})"

	def get_sid(self):
		return self.sid

	def captured(self) -> dict:
		capture = dict()
		capture['sid'] = self.sid
		return capture