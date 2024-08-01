import json


def write_to_file(filename, root_obj):
	# visualize the data in a file
	data = root_obj.display_json()
 
	with open(filename, 'w') as outfile:
		#outfile.write(cmd)
		json.dump(data, outfile, indent=4)
	return