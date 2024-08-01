import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfounddistinguishednamefordomainuser import Filtered_FoundDistinguishedNameForDomainUser
from COMPONENTS.filteredobjects.filteredfounduserprincipalnamefordomainuser import Filtered_FoundUserPrincipalNameForDomainUser


def create_filtered_objects_from_user_records_of_list_users_windapsearch(user_record:dict):
	"""
	Filters the filtered objects out from the information
	we receive for each user
	"""
	filtered_objects = list()
 
	if 'sAMAccountName' in user_record:
		# username = sAMAccountName; unique for domain
		username = user_record['sAMAccountName']
		if 'dn' in user_record:
			# found distinguished name for this user
			distinguished_name = user_record['dn']
			fo = Filtered_FoundDistinguishedNameForDomainUser(username, distinguished_name)
			filtered_objects.append(fo)
		if 'userPrincipalName' in user_record:
			# found user principal name for this user
			user_principal_name = user_record['userPrincipalName']
			fo = Filtered_FoundUserPrincipalNameForDomainUser(username, user_principal_name)
			filtered_objects.append(fo)
   
	return filtered_objects


class RetrieveListUsersWithWindapsearch_Filter(AbstractFilter):
	_name = "Filter list of users with windapsearch"
	
	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []
		current_user = {}
		
		for line in output.strip().split('\n'):
			if not line.strip():  # Empty line indicates new record
				if current_user:
					# parse the information we found for the user.
					# our identifier is the sAMAccountName that is unique
					# in a domain
					fos = create_filtered_objects_from_user_records_of_list_users_windapsearch(current_user)
					for fo in fos:
						findings.append(fo)
					# clear for next user
					current_user = {}
			else:
				# new user information
				key, value = line.split(': ', 1)
				current_user[key] = value
		
		# the last user (if any)
		if current_user:
			fos = create_filtered_objects_from_user_records_of_list_users_windapsearch(current_user)
			for fo in fos:
				findings.append(fo)
			# clear for next user
			current_user = {}
		return findings