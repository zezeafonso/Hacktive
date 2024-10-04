from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundUsernameFromQuery(AbstractFilteredObject):
	def __init__(self, username:str):
		self.username = username # True|False

	def display(self):
		return f"Found user name: ({self.username})"

	def get_username(self):
		return self.username

	def captured(self) -> dict:
		capture = dict()
		capture['username'] = self.username
		return capture