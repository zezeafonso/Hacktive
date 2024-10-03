import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter
from COMPONENTS.filteredobjects.filteredfounddomainuserthroughrpc import Filtered_FoundDomainUserThroughRPC
from COMPONENTS.filteredobjects.filteredfoundusernamefromqueryuser import Filtered_FoundUsernameFromQuery
from COMPONENTS.filteredobjects.filteredfounddescriptionofdomainuser import Filtered_FoundDescriptionOfDomainUser
from COMPONENTS.filteredobjects.filteredfounddomainuserridthroughrpc import Filtered_FoundDomainUserRidThroughRPC

class EnumDomUsersThroughRPC_Filter(AbstractFilter):
	_name = "filter enum domain users through rpc"

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
			username_match = username_pattern.match(line)
			description_match = description_pattern.match(line)
			user_rid_match = user_rid_pattern.match(line)
			if username_match:
				username = username_match.group(1)
				list_fo.append(Filtered_FoundUsernameFromQuery(username))
			elif description_match:
				description = description_match.group(1)
				list_fo.append(Filtered_FoundDescriptionOfDomainUser(description))
			elif user_rid_match: 
				user_rid = user_rid_match.group(1)	
				list_fo.append(Filtered_FoundDomainUserRidThroughRPC(user_rid))
		return list_fo