from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainTrust(AbstractFilteredObject):
	def __init__(self, domain_name:str):
		self.info = dict()
		self.info['domain_name'] = domain_name

	def display(self):
		return f"new domain trust for domain ({self.get_domain_name()})"

	def get_domain_name(self):
		return self.info['domain_name']

	def captured(self) -> dict:
		return self.info