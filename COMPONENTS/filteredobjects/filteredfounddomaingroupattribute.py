from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainGroupAttribute(AbstractFilteredObject):
	def __init__(self, groupname:str, attribute_name:str, attribute_value:str):
		# the username should be the sAMAccountName
		self.groupname = groupname
		self.name = attribute_name
		self.value = attribute_value

	def display(self):
		return f"Found new domain attribute ({self.name}) with value ({self.value}) \
      for domain group ({self.get_groupname()})"

	def get_groupname(self):
		return self.groupname

	def get_attr_name(self):
		return self.name

	def get_attr_value(self):
		return self.value

	def captured(self) -> dict:
		return {'groupname':self.groupname, 'attr_name':self.name, 'attr_value':self.value}