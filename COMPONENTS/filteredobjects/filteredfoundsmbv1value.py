from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundSMBv1Value(AbstractFilteredObject):
	def __init__(self, value:str):
		self.smbv1 = value # True|False

	def display(self):
		return f"Found if smbv1 was enabled: ({self.value})"

	def get_smbv1_value(self):
		return self.smbv1

	def captured(self) -> dict:
		capture = dict()
		capture['smbv1'] = self.smbv1
		return capture