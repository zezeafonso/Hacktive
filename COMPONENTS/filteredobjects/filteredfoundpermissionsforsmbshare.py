from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundPermissionsForSMBShare(AbstractFilteredObject):
	def __init__(self, share_name:str, permissions:str):
		self.share_name = share_name 
		self.permissions = permissions

	def display(self):
		return f"Found share description: ({self.permissions}) for share: ({self.share_name})"

	def get_share_name(self):
		return self.share_name

	def get_permissions(self): 
		return self.permissions

	def captured(self) -> dict:
		capture = dict()
		capture['share_name'] = self.share_name
		capture['permissions'] = self.permissions
		return capture