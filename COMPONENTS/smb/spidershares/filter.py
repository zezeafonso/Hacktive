import re

from COMPONENTS.abstract.abstractfilter import AbstractFilter

from COMPONENTS.filteredobjects.filteredfoundpermissionsforsmbshare import Filtered_FoundPermissionsForSMBShare

class SpiderSharesThroughSMB_Filter(AbstractFilter):
	_name = "filter spider shares through SMB"

	@staticmethod
	def filter(output:str) -> list:
		list_fo = list()

		for line in output.splitlines():
			# Check if the line contains the permissions and share name
			if 'NO ACCESS' in line or 'READ ONLY' in line or 'READ, WRITE' in line:
				parts = line.split()
				share_name = parts[0]
				permission = " ".join(parts[1:3])
				list_fo.append(Filtered_FoundPermissionsForSMBShare(share_name, permission))
		return list_fo