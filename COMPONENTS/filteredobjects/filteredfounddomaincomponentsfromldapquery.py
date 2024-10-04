from COMPONENTS.abstract.abstractfilteredobj import AbstractFilteredObject

class Filtered_FoundDomainComponentsFromLDAPQuery(AbstractFilteredObject):
	def __init__(self, path:dict, list_dc:list):
		self.info = dict()
		self.info['path'] = path

		# create the path ex: foxriver.local
		domain_components_path = ''
		for dc in list_dc:
			domain_components_path += dc + '.'
		domain_components_path = domain_components_path[:-1] # remove the final dot
		
		self.info['dc_path'] = domain_components_path

	def display(self):
		return f"Found Domain Components Path ({self.info['dc_path']})"

	def captured(self) -> dict:
		return self.info

	def get_dc_path(self):
		return self.info['dc_path']