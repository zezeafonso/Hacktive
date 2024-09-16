from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_founddefaultnamingcontext(AbstractFilteredObject):
	def __init__(self, naming_context:str):
		self.naming_context = naming_context # ex: foxriver.local

	def display(self):
		return f"Found Default Naming Context ({self.naming_context})"

	def captured(self) -> dict:
		return {'naming context':self.naming_context}

	def get_naming_context(self):
		return self.naming_context