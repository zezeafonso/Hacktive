import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfounddomainuserattribute import Filtered_FoundDomainUserAttribute
from COMPONENTS.filteredobjects.filteredfounddomaingroupattribute import Filtered_FoundDomainGroupAttribute


def filter_group_attributes(chunk_lines):
	"""
 	filter group information from a chunk of lines of the 
  	output marked by:
   	dn: 
    	
    """
	group_info = dict()
	findings = list()
 
	# for each output line
	for line in chunk_lines:
		if 'description:' in line:
			group_info['description'] = line.split('description: ')[1].strip()
		elif 'objectGUID:' in line:
			group_info['objectGUID'] = line.split('objectGUID: ')[1].strip()
		elif 'objectSid:' in line:
			group_info['objectSid'] = line.split('objectSid: ')[1].strip()
		elif 'sAMAccountName:' in line:
			groupname = line.split('sAMAccountName: ')[1].strip()
		elif 'userPrincipalName:' in line:
			group_info['userPrincipalName'] = line.split('userPrincipalName: ')[1].strip()
		elif 'distinguishedName' in line:
			group_info['distinguishedName'] = line.split('distinguishedName: ')[1].strip()

	# nothing to do for this user
	if groupname is None:
		return []

	# after parsing, for every attribute
	for attr_name in group_info:
		# create the filtered object for the attribute
		fo = Filtered_FoundDomainGroupAttribute(groupname, attr_name, group_info[attr_name])
		findings.append(fo)
  
	return findings



def filter_user_attributes(chunk_lines):
	"""
 	filter user information from a chunk of lines of the 
  	output marked by:
   	dn: 
    	
    """
	user_info = dict()
	findings = list()
	
	# for each output line
	for line in chunk_lines:
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
		elif 'distinguishedName' in line:
			user_info['distinguishedName'] = line.split('distinguishedName: ')[1].strip()

	# nothing to do for this user
	if username is None:
		return []

	# after parsing, for every attribute
	for attr_name in user_info:
		# create the filtered object for the attribute
		fo = Filtered_FoundDomainUserAttribute(username, attr_name, user_info[attr_name])
		findings.append(fo)
  
	return findings



class GetAllLdap_Filter(AbstractFilter):
	"""
 	Abstract class responsible for filtering the output
  	of the get all ldap information through nmap
   	"""
	_name = "Filter list all ldap information with nmap"
	
	@staticmethod
	def filter(output:str) -> list: 
		# the list of filtered objects we find
		findings = []

		# split the output in chunks of information for each user
		chunks = output.split('dn: ')[1:]

		for chunk in chunks:
			lines = chunk.strip().split('\n')
			
			# for each line of a chunk (DN: )
			for line in lines[1:]:
				# parse the information according to its type
				if 'objectClass' in line:
					value = line.split('objectClass: ')[1].strip()
					# user type 
					if value == 'user':
						findings += filter_user_attributes(chunk)
						break 
					# group 
					if value == 'group':
						findings += filter_group_attributes(chunk)
						break
					# nothing else for now
					else:
						continue # check next line
     
		return findings