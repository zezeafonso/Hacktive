import threading 
import subprocess
import queue
import logging

import ThreadShares as TS
import Filters
import SpecificExceptions as SE
from LoggingConfig import logger
import NetworkComponentUpdater as NCU
import MethodsToFilters
import output_json as OJ


commands_and_filtered_objs = dict()

def str_display_from_list_filtered(filtered_objs : list):
	filtered_obj_display = ""
	for f_obj in filtered_objs:
		filtered_obj_display += f_obj.display()+';'
	return filtered_obj_display


def print_commands_and_filtered_objects():
	global commands_and_filtered_objs
	display = ''

	for cmd in commands_and_filtered_objs:
		display_fo = str_display_from_list_filtered(commands_and_filtered_objs[cmd])
		display += f"\n----\n({cmd}) : \n"+display_fo

	print(display)


def print_state_network_components_after_cmd(cmd):
	with TS.shared_lock:
		cmd_without_strings = cmd.replace(' ', '')
		cmd_without_slashes = cmd_without_strings.replace('/', '-')
		cmd_without_dots = cmd_without_slashes.replace('.', '-')
		filename = 'states/JSON-'+cmd_without_dots+'.json'
		OJ.write_to_file(filename, root_obj)


def analyze_event(event):
	"""
	Defines what we do when an event was received.
	The attributes of the methos are retrieved
	the filter for the method is retrieved
	the output is filtered
	the network components get updated depending on the filtered_objects
	the auto_functions are returned
	"""
	global commands_and_filtered_objs
	global root_obj

	# extract the fields from event
	output = event.output
	method = event.method
	nc = event.network_component
	context = event.context
	cmd = event.command

	# know the correct filter
	f = MethodsToFilters.methods_to_filters[method]
	logger.debug(f" filtering output in: {f._name}")

	list_filtered_objects = f.filter(output) # returns filtered objects

	TS.remove_command_from_commands_to_analyze(cmd)

	logger.debug(f"filtered objects from ({cmd}): {str_display_from_list_filtered(list_filtered_objects)}")
	commands_and_filtered_objs[cmd] = list_filtered_objects

	if list_filtered_objects != []:
		# update the network components with these captured information from the filter
		auto_functions = NCU.update_network_components(method, context, list_filtered_objects)

		# print the state of the network components after the update network components
		print_state_network_components_after_cmd(cmd)

		if auto_functions is None:
			return []
		return auto_functions
	else:
		return []


def outputs_listener(root):
	# init the network components dictionary
	Filters.init_dictionaries()
	logger.info(" up")

	global commands_and_filtered_objs
	global root_obj

	root_obj = root

	while True:
		event = TS.out_queue.get() # BLOCKING call, wait for outputs
		logger.debug(" Received Event")

		# Sentinel to exit
		if event == 'Done':  
			logger.info(" Finishing...")
			print_commands_and_filtered_objects()
			break

		# EXCEPTION
		if event.type != 'done':
			continue

		# RECEIVED CORRECT EVENT ---
		auto_functions = analyze_event(event)
		for auto_function in auto_functions:
			logger.debug(f"calling auto function: ({auto_function})")
			auto_function()

		if TS.out_queue.empty(): 
			logger.debug(f"No outputs to parse, queue is empty")
			TS.cmd_queue.put('Done')

		TS.out_queue.task_done()

	return