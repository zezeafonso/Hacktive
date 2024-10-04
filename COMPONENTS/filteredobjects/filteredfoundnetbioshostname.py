from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundNetBIOSHostname(AbstractFilteredObject):
	def __init__(self, hostname:str):
		self.hostname = hostname # True|False

	def display(self):
		return f"Found hostname: ({self.hostname})"

	def get_hostname(self):
		return self.hostname

	def captured(self) -> dict:
		capture = dict()
		capture['hostname'] = self.hostname
		return capture