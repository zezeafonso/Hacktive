import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfounddomainuserattribute import Filtered_FoundDomainUserAttribute


def filter_group_info_from_chunk(chunk):
	findings = list()
	lines = chunk.strip().split('\n')
			
	# Extract the 'dn' line
	groupname = None
	dn = lines[0].strip()
	group_info = dict()
	for line in lines:
		if 'description:' in line:
			group_info['description'] = line.split('description: ')[1].strip()
		elif 'objectGUID:' in line:
			group_info['objectGUID'] = line.split('objectGUID: ')[1].strip()
		elif 'objectSid:' in line:
			group_info['objectSid'] = line.split('objectSid: ')[1].strip()
		elif 'sAMAccountName:' in line:
			groupname = line.split('sAMAccountName: ')[1].strip()
		elif 'distinguishedName' in line:
			group_info['distinguishedName'] = line.split('distinguishedName: ')[1].strip()
	
	if groupname is None:
		return findings

	# after parsing, for every attribute
	for attr_name in group_info:
		# create the filtered object for the attribute
		fo = Filtered_FoundDomainUserAttribute(groupname, attr_name, group_info[attr_name])
		findings.append(fo)
	
	return findings



def filter_user_info_from_chunk(chunk):
	findings = list()
	lines = chunk.strip().split('\n')
			
	# Extract the 'dn' line
	dn = lines[0].strip()
	user_info = dict()
	for line in lines:
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
		return findings

	# after parsing, for every attribute
	for attr_name in user_info:
		# create the filtered object for the attribute
		fo = Filtered_FoundDomainUserAttribute(username, attr_name, user_info[attr_name])
		findings.append(fo)
	
	return findings
	
 


class GetAllLdap_Filter(AbstractFilter):
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
				if 'objectClass' in line:
					o_class = line.split('objectClass: ')[1].strip()
					if o_class == 'user':
						findings += filter_user_info_from_chunk(chunk)
						break
					elif o_class == 'group':
						findings += filter_group_info_from_chunk(chunk)
						break
					else:
						continue
     
		return findings