from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundSMBServerVersion(AbstractFilteredObject):
	def __init__(self, version:str):
		self.version = version 

	def display(self):
		return f"Found SMB server version: ({self.version})"

	def get_server_version(self):
		return self.version

	def captured(self) -> dict:
		capture = dict()
		capture['version'] = self.version
		return capture