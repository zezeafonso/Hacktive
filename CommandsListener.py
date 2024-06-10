import subprocess
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import logging

from MethodsToFilters import methods_to_filters
import SpecificExceptions as SE
from Events import Done_Event
import ThreadShares as TS
from AbstractClasses import AbstractNetworkComponent, AbstractFilter, AbstractMethod
import LoggingConfig



def run_normal_command(out_file:str, cmd:str, nc:AbstractNetworkComponent, method:AbstractMethod, context:dict):
	# call Popen
	logging.info(f"[Pool thread]: calling Popen for command: {cmd}")

	# add to the list of commands already run 
	TS.add_command_to_commands_run(cmd)

	# run the commands in parallel using a different process
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

	# Store the PID
	pid = proc.pid
	try: 
		logging.info(f"[Pool thread {cmd}]: storing PID: {pid}")
		TS.add_pid_to_cmd_pid_dict(cmd, pid, TS.shared_lock)
	except SE.CommandAlreadyBeingRun as e:
		raise Exception(f"Command {cmd} is already being run")

	# Wait for the process to complete and get output
	stdout, stderr = proc.communicate() # BLOCKING CALL (thread)
	logging.info(f"[Pool thread {cmd}] received output. Return code = {proc.returncode}")

	# remove pid from list of running processes
	try:
		TS.del_pid_from_cmd_pid_dict(cmd, pid, TS.shared_lock)
	except SE.CommandNotBeingRun as e:
		raise Exception(f"Command {cmd} was not being run")

	# retrieve the output
	output = stdout if proc.returncode == 0 else stderr

	# write the output to the file
	try:
		filename = out_file
		logging.info(f"[Pool thread {cmd}] writting to file: {filename}")
		with open(filename, 'w') as file:
			file.write(output)
	except FileNotFoundError as e:
		raise Exception("File Not Found")

	# create the event done (only with stdout)
	output_event = Done_Event('done',cmd, stdout, method, nc, context)

	# put it in the queue for outputs_listener thread
	TS.out_queue.put(output_event)
	logging.info(f"[Pool thread {cmd}] sended Done Event to outputs")

	return stdout



def commands_listener(thread_pool:ThreadPoolExecutor):
	LoggingConfig.configure_logging()
	logging.info(f"[Commands listener]: up")

	while True:
		# get an event from the commands_queue
		event = TS.cmd_queue.get()
		logging.info(f"[Commands Listener]: received event")

		# output thread sent done (it had no more outputs to parse)
		# if we have no more methods in the queue, and all the methods 
		# already sent were processed than finish.
		if event == 'Done':
			# if there is no comamnd for analysis and no command to be read from the queue -> finish
			if TS.cmd_queue.empty() and TS.check_if_there_are_no_commands_for_analysis():
				logging.info("[Commands Listener]: Finishing...")
				logging.info("[Commands Listener]: shutting down the pool")
				thread_pool.shutdown(wait=True)
				TS.out_queue.put('Done') # sentinel to outputs queue
				logging.info("[Commands Listener: sending 'Done' to output]")
				break
		else:
			# event must be of type run
			if event.type != 'run':
				raise SE.CommandsListenerReceiveNonRunEvent()
			
			# know the events attributes
			out_file, cmd, method, nc, context = event.get_attributes()

			# if commands wasn't already run
			if not TS.know_if_commands_was_already_run(cmd):
				# add commands to the list of commands for analysis
				TS.add_command_to_commands_for_analysis(cmd)

				# submit task to pool
				thread_pool.submit(run_normal_command, out_file, cmd, nc, method, context)
				logging.info(f"[Commands Listener] submitted to the pool: {cmd}")
			else:
				print(f"{cmd} was already run!!!!")

			# task done
			TS.cmd_queue.task_done()
	
	#TS.cmd_queue.join() # every command inserted
	return