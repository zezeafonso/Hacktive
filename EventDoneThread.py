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





def outputs_listener():
	# init the network components dictionary
	Filters.init_dictionaries()
	logger.info("[Output Listener]: up")

	while True:
		event = TS.out_queue.get() # BLOCKING call, wait for outputs
		logger.debug("[Output Listener]: Received Event")

		# Sentinel to exit
		if event == 'Done':  
			logger.info("[Output Listener]: Finishing...")
			break

		# EXCEPTION
		if event.type != 'done':
			continue

		# RECEIVED CORRECT EVENT ---

		# extract the fields from event
		output = event.output
		method = event.method
		nc = event.network_component
		context = event.context
		cmd = event.command

		# know the correct filter
		f = MethodsToFilters.methods_to_filters[method]
		# log
		logger.debug(f"[Output Listener]: filtering output in: {f._name}")

		# filter the contents of the output for objects
		list_filtered_objects = f.filter(output) # it will create the objects

		# remove this commands from the list of commands to analyze
		TS.remove_command_from_commands_to_analyze(cmd)

		print(list_filtered_objects)
		if list_filtered_objects != []:
			# update the network components with these captured information from the filter
			auto_methods = NCU.update_network_components(method, context, list_filtered_objects)
			if auto_methods is None:
				auto_methods = []

			# call the correct auto methods -> only objects newly created 
			print(auto_methods)
			for method in auto_methods:
				print(f"calling method {method}")
				# call the automatic methods (will put events in cmd_queue)
				method() 

			# no more outputs to parse for now -> send to the commands thread this is done
			if TS.out_queue.empty(): 
				TS.cmd_queue.put('Done')
		else:
			# no more outputs to parse for now -> send to the commands thread this is done
			if TS.out_queue.empty(): 
				TS.cmd_queue.put('Done')

		# this output was treated	
		TS.out_queue.task_done()

	return