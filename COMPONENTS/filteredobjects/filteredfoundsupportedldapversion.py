from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundSupportedLdapVersion(AbstractFilteredObject):
	def __init__(self, value:str):
		self.version = value # True|False

	def display(self):
		return f"Found supported ldap version: ({self.version})"

	def get_version(self):
		return self.version

	def captured(self) -> dict:
		return {'version':self.version}