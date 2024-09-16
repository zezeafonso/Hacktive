from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainOfMachine(AbstractFilteredObject):
	def __init__(self, domain_name:str):
		self.domain_name = domain_name # True|False

	def display(self):
		return f"Found domain name of machine ({self.domain_name})"

	def get_domain_name(self):
		return self.domain_name

	def captured(self) -> dict:
		capture = dict()
		capture['domain_name'] = self.domain_name
		return capture