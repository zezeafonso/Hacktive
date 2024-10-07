from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundPolicyForLdapServer(AbstractFilteredObject):
	def __init__(self, policy:str):
		self.policy = policy

	def display(self):
		return f"Found LDAP policy: ({self.policy})"

	def get_policy(self):
		return self.policy

	def captured(self) -> dict:
		capture = dict()
		capture['policy'] = self.policy
		return capture