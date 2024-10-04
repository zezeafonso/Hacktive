from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundSMBShareDescriptionForShareName(AbstractFilteredObject):
	def __init__(self, share_name:str, description:str):
		self.share_name = share_name 
		self.description = description

	def display(self):
		return f"Found share description: ({self.description}) for share: ({self.share_name})"

	def get_share_name(self):
		return self.share_name

	def get_description(self): 
		return self.description

	def captured(self) -> dict:
		capture = dict()
		capture['share_name'] = self.share_name
		capture['description'] = self.description
		return capture