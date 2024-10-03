import THREADS.sharedvariables as SV
from LOGGER.loggerconfig import logger
import output_json as OJ



commands_and_filtered_objs = dict()

def str_display_from_list_filtered(filtered_objs : list):
	filtered_obj_display = ""
	for f_obj in filtered_objs:
		filtered_obj_display += f_obj.display()+';\n'
	return filtered_obj_display


def print_commands_and_filtered_objects():
	global commands_and_filtered_objs
	display = ''

	for cmd in commands_and_filtered_objs:
		display_fo = str_display_from_list_filtered(commands_and_filtered_objs[cmd])
		display += f"\n----\n({cmd}) : \n"+display_fo

	print(display)


# Example function to showcase results
def display_command_results(cmd, findings, success=True):
    print(f"\n[>] {cmd}")

    if success:
        print("\033[92m" + "Findings:" +"\033[0m")
        for finding in findings:
            print("\033[92m" + f"  - {finding.display()}" + "\033[0m")
    else:
        print("\033[91m"+" Command produced Non 0 output"+"\033[0m")


def print_state_network_components_after_cmd(cmd):
	with SV.shared_lock:
		cmd_without_strings = cmd.replace(' ', '')
		cmd_without_slashes = cmd_without_strings.replace('/', '-')
		cmd_without_dots = cmd_without_slashes.replace('.', '-')
		filename = 'states/JSON-'+cmd_without_dots+'.json'
		OJ.write_to_file(filename, SV.root_obj)


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

	# extract the fields from event
	output = event.output
	return_code = event.return_code
	method = event.method
	context = event.context
	cmd = event.command

	# error cases:
	# THE COMMAND WASN'T SUCCESSFULL
	if return_code != 0:
		logger.warning(f"({cmd}) produced a non 0 return code")
		# NOTE: super important so that commands thread knows this is done
		SV.remove_command_from_commands_to_analyze(cmd)
		
		commands_and_filtered_objs[cmd] = []
		# NOTE: the state was just for debug
		#print_state_network_components_after_cmd(cmd) # for the states 
		display_command_results(cmd, [], False)
		#display = f"\n----\n({cmd}) : \nProduced a non 0 return code"
		#print(display)
		return

	# know the correct filter
	f = method._filter
	func_update = method._updater

	logger.debug(f" filtering output in: {f._name}")
	list_filtered_objects = f.filter(output) # returns filtered objects
	logger.debug(f"filtered objects from ({cmd}): {str_display_from_list_filtered(list_filtered_objects)}")


	# to know what we extrapolated from the output of the command
	commands_and_filtered_objs[cmd] = list_filtered_objects
	# no succesfull filter
	if list_filtered_objects == []: 
		# NOTE: super important so that commands thread knows this is done
		SV.remove_command_from_commands_to_analyze(cmd)
		# nothing to update
		# states are the same as before
		display_command_results(cmd, list_filtered_objects, True)
		#display = f"\n----\n({cmd}) : \n"
		#print(display)
		return 

	# update the network components with these captured information from the filter
	func_update(context, list_filtered_objects)

	# print the state of the network components after the update network components
	# NOTE: the state is only used for debug
	# print_state_network_components_after_cmd(cmd)
	
	display_command_results(cmd, list_filtered_objects, True)
	#display_fo = str_display_from_list_filtered(list_filtered_objects)
	#display = f"\n----\n({cmd}) : \n"+display_fo
	#print(display)
	
	# NOTE: super important so that commands thread knows this is done
	SV.remove_command_from_commands_to_analyze(cmd)
	
	return


def outputs_listener():
	# init the network components dictionaryW
	logger.info(" up")

	global commands_and_filtered_objs

	while True:
		event = SV.out_queue.get() # BLOCKING call, wait for outputs
		logger.debug(" Received Event")

		# Sentinel to exit
		if event == 'Done':  
			logger.info(" Finishing...")
			#print_commands_and_filtered_objects()
			break

		# EXCEPTION
		if event.type != 'done':
			continue

		# RECEIVED CORRECT EVENT ---
		analyze_event(event)

		# if no more events to analyze for now
		if SV.out_queue.empty(): 
			logger.debug(f"No outputs to parse, queue is empty")
			SV.cmd_queue.put('Done')

		SV.out_queue.task_done()

	return