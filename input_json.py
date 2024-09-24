import json

def read_config_methods():
	with open('COMPONENTS/config/methods.json', 'r') as file:
		json_data = json.load(file)
	return json_data
	
