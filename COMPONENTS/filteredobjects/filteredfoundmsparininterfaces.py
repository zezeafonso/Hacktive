from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject


class Filtered_FoundMSPARInInterfaces(AbstractFilteredObject):
	def __init__(self):
		self.found = True

	def display(self):
		return f"Found protocol [MS-PAR] in interface listing"

	def captured(self):
		return 