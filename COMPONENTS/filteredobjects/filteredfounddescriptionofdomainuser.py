from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDescriptionOfDomainUser(AbstractFilteredObject):
	def __init__(self, description:str):
		self.description = description # True|False

	def display(self):
		return f"Found user description: ({self.description})"

	def get_description(self):
		return self.description

	def captured(self) -> dict:
		capture = dict()
		capture['description'] = self.description
		return capture