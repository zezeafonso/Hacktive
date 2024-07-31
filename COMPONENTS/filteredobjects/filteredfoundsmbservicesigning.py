from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundSMBServiceSigning(AbstractFilteredObject):
	def __init__(self, signing:str):
		self.signing = signing # True|False

	def display(self):
		return f"Found if signing was required: ({self.signing})"

	def get_signing_value(self):
		return self.signing

	def captured(self) -> dict:
		capture = dict()
		capture['signing'] = self.signing
		return capture