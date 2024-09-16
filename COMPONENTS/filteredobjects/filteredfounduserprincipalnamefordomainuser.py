from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundUserPrincipalNameForDomainUser(AbstractFilteredObject):
	def __init__(self, sam_account_name:str, user_principal_name:str):
		self.username = sam_account_name # unique for a domain
		self.user_principal_name = user_principal_name 

	def display(self):
		return f"Found user principal name: ({self.user_principal_name}) for user: ({self.username})"

	def captured(self) -> dict:
		return {'user principal name':self.user_principal_name, \
      			'sAMAccountName':self.username}

	def get_user_principal_name(self):
		return self.user_principal_name

	def get_sam_account_name(self):
		return self.username