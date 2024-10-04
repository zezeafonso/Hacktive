import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomainuserridthroughrpc import Filtered_FoundDomainUserRidThroughRPC
from COMPONENTS.filteredobjects.filteredfoundusernamefromqueryuser import Filtered_FoundUsernameFromQuery
from COMPONENTS.filteredobjects.filteredfounddescriptionofdomainuser import Filtered_FoundDescriptionOfDomainUser
from COMPONENTS.filteredobjects.filteredfounddomainuserridthroughrpc import Filtered_FoundDomainUserRidThroughRPC

class RetrieveUserInformationThroughRPC_Filter(AbstractFilter):
	"""
	For now we are just parsing the RID from this output
	"""
	_name = "filter retrieve information from user through rpc"

	@staticmethod
	def filter(output:str) -> list: 
		# Define a regex pattern to capture sharename, type, and comment from each line
		username_pattern = re.compile(r"User Name\s*:\s*(\S+)")
		description_pattern = re.compile(r"Description\s*:\s*(.*)")
		user_rid_pattern = re.compile(r"user_rid\s*:\s*(\S+)")
		
		# the list of filtered objects
		list_fo = list()
		
		# Split the output by lines and iterate through each line
		for line in output.splitlines():
			# Try to match the line against the pattern
			username_match = username_pattern.search(line)
			description_match = description_pattern.search(line)
			user_rid_match = user_rid_pattern.search(line)
			if username_match:
				username = username_match.group(1)
				list_fo.append(Filtered_FoundUsernameFromQuery(username))
			elif description_match:
				description = description_match.group(1)
				list_fo.append(Filtered_FoundDescriptionOfDomainUser(description))
			elif user_rid_match: 
				user_rid = user_rid_match.group(1)	
				rid_hex_str = str(user_rid)
				list_fo.append(Filtered_FoundDomainUserRidThroughRPC(rid_hex_str))
		return list_fo

	"""
	@staticmethod
	def filter(output:str) -> list:
		findings = list()
		# Define a regular expression pattern
		pattern = re.compile(r"user_rid:\s+(0x[0-9a-fA-F]+)")

		# Iterate over each line and search for matches
		for line in output.splitlines():
			match = pattern.search(line)
			if match:
				rid_hex = match.group(1)
				rid_hex_str = str(rid_hex)

				findings.append(Filtered_FoundDomainUserRidThroughRPC(rid_hex_str))
		return findings
	"""