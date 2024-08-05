import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfounddomainuserattribute import Filtered_FoundDomainUserAttribute

class GetUsersLdap_Filter(AbstractFilter):
	_name = "Filter list of users with windapsearch"
	
	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		# split the output in chunks of information for each user
		chunks = output.split('dn: ')[1:]

		for chunk in chunks:
			user_info = {}
			lines = chunk.strip().split('\n')
			
			# Extract the 'dn' line
			user_info['dn'] = lines[0].strip()
			username = None
			
			# Extract fields
			for line in lines[1:]:
				if 'description:' in line:
					user_info['description'] = line.split('description: ')[1].strip()
				elif 'objectGUID:' in line:
					user_info['objectGUID'] = line.split('objectGUID: ')[1].strip()
				elif 'objectSid:' in line:
					user_info['objectSid'] = line.split('objectSid: ')[1].strip()
				elif 'sAMAccountName:' in line:
					username = line.split('sAMAccountName: ')[1].strip()
				elif 'userPrincipalName:' in line:
					user_info['userPrincipalName'] = line.split('userPrincipalName: ')[1].strip()
     
			if username is None:
				continue # nothing to do for this user

			# after parsing, for every attribute
			for attr_name in user_info:
				# create the filtered object for the attribute
				fo = Filtered_FoundDomainUserAttribute(username, attr_name, user_info[attr_name])
				findings.append(fo)
     
		return findings