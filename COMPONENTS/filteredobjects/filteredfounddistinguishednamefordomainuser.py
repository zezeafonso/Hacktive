from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDistinguishedNameForDomainUser(AbstractFilteredObject):
	def __init__(self, sam_account_name:str, distinguished_name:str):
		self.username = sam_account_name # unique for a domain
		self.dn = distinguished_name 

	def display(self):
		return f"Found distinguished name: ({self.dn}) for user: ({self.username})"

	def captured(self) -> dict:
		return {'distinguished name':self.dn, 'sAMAccountName':self.username}

	def get_distinguished_name(self):
		return self.dn

	def get_sam_account_name(self):
		return self.username