from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainUserAttribute(AbstractFilteredObject):
	def __init__(self, username:str, attribute_name:str, attribute_value:str):
		# the username should be the sAMAccountName
		self.username = username
		self.name = attribute_name
		self.value = attribute_value

	def display(self):
		return f"new domain attribute ({self.name}) with value ({self.value}) \
      for domain user ({self.get_domain_name()})"

	def get_username(self):
		return self.username

	def get_attr_name(self):
		return self.name

	def get_attr_value(self):
		return self.value

	def captured(self) -> dict:
		return {'username':self.username, 'attr_name':self.name, 'attr_value':self.value}