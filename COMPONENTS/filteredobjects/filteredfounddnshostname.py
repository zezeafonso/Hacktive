from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_founddnshostname(AbstractFilteredObject):
	def __init__(self, dns_hostname:str):
		self.dns_hostname = dns_hostname # ex: foxriver.local

	def display(self):
		return f"Found DNS hostname ({self.dns_hostname})"

	def captured(self) -> dict:
		return {'dns hostname':self.dns_hostname}

	def get_dns_hostname(self):
		return self.dns_hostname