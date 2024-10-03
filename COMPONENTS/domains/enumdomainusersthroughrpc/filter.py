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
		list_fo = list()
  
		# Define a regular expression pattern
		# Define regex patterns to extract needed information
		username_pattern = r"User Name\s*:\s*(\S+)"
		description_pattern = r"Description\s*:\s*(.*)"
		user_rid_pattern = r"user_rid\s*:\s*(\S+)"

		# Extract using regex
		username = re.search(username_pattern, output).group(1)
		description = re.search(description_pattern, output).group(1)
		user_rid = re.search(user_rid_pattern, output).group(1)
		
		list_fo.append(Filtered_FoundUsernameFromQuery(username))
		list_fo.append(Filtered_FoundDescriptionOfDomainUser(description))
		list_fo.append(Filtered_FoundDomainUserRidThroughRPC(user_rid))

		return list_fo