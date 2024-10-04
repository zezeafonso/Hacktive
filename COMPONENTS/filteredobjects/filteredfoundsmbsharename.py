from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundSMBShareName(AbstractFilteredObject):
	def __init__(self, share_name:str):
		self.share_name = share_name 

	def display(self):
		return f"Found share: ({self.share_name})"

	def get_share_name(self):
		return self.share_name

	def captured(self) -> dict:
		capture = dict()
		capture['share_name'] = self.share_name
		return capture