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
from LoggingConfig import logger


def get_event_from_the_command_queue():
	event = TS.cmd_queue.get() # blocking
	logger.debug(f"received event")
	return event

def send_sentinel_to_output_listener_thread():
	TS.out_queue.put('Done')

def handle_done_events_from_output_listener_thread(thread_pool):
	# if there is no command for analysis and no command to be read from the queue -> finish
	if TS.cmd_queue.empty() and TS.check_if_there_are_no_commands_for_analysis():
		logger.info("Finishing...")
		logger.info("shutting down the pool")

		thread_pool.shutdown(wait=True) # shutdown the pool
		send_sentinel_to_output_listener_thread()

		logger.info("sending 'Done' to output")
		return 0
	return 1

def run_command_in_another_process(cmd):
	logger.debug(f"[Pool thread]: calling Popen for command: {cmd}")

	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
	return proc


def store_the_pid_of_process_in_pids_executing_commands(cmd, pid):
	try: 
		logger.debug(f"[Pool thread {cmd}]: storing PID: {pid}")

		TS.add_pid_to_cmd_pid_dict(cmd, pid, TS.shared_lock)
	except SE.CommandAlreadyBeingRun as e:
		raise Exception(f"Command {cmd} is already being run")


def wait_for_process_to_complete_and_get_output_and_err(proc):
	# Wait for the process to complete and get output
	stdout, stderr = proc.communicate() # BLOCKING CALL (thread)

	logger.debug(f"[Pool thread {proc.pid}] received output. Return code = {proc.returncode}")
	return stdout, stderr


def remove_the_pid_of_process_from_the_pids_executing_commands(cmd, pid):
	# remove pid from list of running processes
	try:
		TS.del_pid_from_cmd_pid_dict(cmd, pid, TS.shared_lock)
	except SE.CommandNotBeingRun as e:
		raise Exception(f"Command {cmd} was not being run")


def write_output_of_command_to_its_respective_file(out_file, pid, output):
	try:
		logger.debug(f"[Pool thread {pid}] writting to file: {out_file}")
		with open(out_file, 'w') as file:
			file.write(output)
	except FileNotFoundError as e:
		raise Exception("File Not Found")

def create_event_for_output_listener(cmd, output, method, nc, context):
	return Done_Event('done', cmd, output, method, nc, context)

def send_event_to_output_listener(event):
	TS.out_queue.put(event)
	logger.debug(f"[Pool thread {cmd}] sended Done Event to outputs")


def thread_pool_run_normal_command(out_file:str, cmd:str, nc:AbstractNetworkComponent, method:AbstractMethod, context:dict):
	TS.add_command_to_list_of_commands_run(cmd)
	proc = run_command_in_another_process(cmd)
	store_the_pid_of_process_in_pids_executing_commands(cmd, proc.pid)
	proc_stdout, proc_stderr = wait_for_process_to_complete_and_get_output_and_err(proc)
	remove_the_pid_of_process_from_the_pids_executing_commands(cmd, proc.pid)
	# know what to send to filter
	output = proc_stdout if proc.returncode == 0 else proc_stderr
	write_output_of_command_to_its_respective_file(out_file, proc.pid, output)
	event = create_event_for_output_listener(cmd, output, method, nc, context)
	send_event_to_output_listener(event)
	return


def submit_new_cmd_to_thread_pool(thread_pool, out_file, cmd, method, nc, context):
	thread_pool.submit(thread_pool_run_normal_command, out_file, cmd, nc, method, context)
	logger.debug(f" submitted to the thread pool: {cmd}")


def handle_normal_command(thread_pool, out_file, cmd, method, nc, context):
	if not TS.know_if_commands_was_already_run(cmd):
		TS.add_command_to_commands_for_analysis(cmd)
		submit_new_cmd_to_thread_pool(thread_pool, out_file, cmd, method, nc, context)
	else:
		logger.warning(f" {cmd} was already run!!")



def commands_listener(thread_pool:ThreadPoolExecutor):
	"""
	Function of the thread that will be listening 
	to command events.

	Should handle the command event and the sentinel from 
	the output thread as well
	"""
	logger.info(f"going inside the while Loop")

	while True:
		event = get_event_from_the_command_queue() # blocking

		# might be sentinel to stop
		if event == 'Done':
			if handle_done_events_from_output_listener_thread(thread_pool) == 0:
				break
		else:
			# event must be of type run
			if event.type != 'run':
				raise SE.CommandsListenerReceiveNonRunEvent()
			
			# know the events attributes
			out_file, cmd, method, nc, context = event.get_attributes()
			handle_normal_command(thread_pool, out_file, cmd, method, nc, context)

			# signal task done
			TS.cmd_queue.task_done()
	
	#TS.cmd_queue.join() # every command inserted
	return