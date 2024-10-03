import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfoundsmbsharename import Filtered_FoundSMBShareName
from COMPONENTS.filteredobjects.filteredfoundsmbsharedescriptionforsharename import Filtered_FoundSMBShareDescriptionForShareName



class ListSharesThroughSMB_Filter(AbstractFilter):
	_name = "filter list sharers through SMB"

	@staticmethod
	def filter(output:str) -> list:
		# Define a regex pattern to capture sharename, type, and comment from each line
		pattern = re.compile(r'^\s*(\S+)\s+(\S+)\s+(.+)$')
		
		# the list of filtered objects
		list_fo = list()
		# Flag to indicate when to start parsing after the separator line
		parsing = False
		
		# Split the output by lines and iterate through each line
		for line in output.splitlines():
			line = line.strip()
			
			# Detect separator and switch parsing mode on
			if '-------' in line:
				parsing = True
				continue
			
			# Once we detect an empty line after the separator, stop parsing
			if parsing and line == "":
				break
			
			# Only parse lines after the separator
			if parsing:
				# Try to match the line against the pattern
				match = pattern.match(line)
				if match:
					sharename = match.group(1)
					share_type = match.group(2)
					comment = match.group(3)
					# dict of information
					list_fo.append(Filtered_FoundSMBShareName(share_name=sharename))
					list_fo.append(Filtered_FoundSMBShareDescriptionForShareName(share_name=sharename, description=comment))
		return list_fo