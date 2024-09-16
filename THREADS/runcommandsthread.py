import subprocess
import copy
from concurrent.futures import ThreadPoolExecutor

from LOGGER.loggerconfig import logger
import EXCEPTIONS.commandexceptions as SE
from THREADS.events import Done_Event
from THREADS.events import Run_Event
import THREADS.sharedvariables as SV
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from LOGGER.loggerconfig import logger



def send_run_event_to_run_commands_thread(run_event:Run_Event):
	"""
	This function is used to send a run_event to the 
	thread that is responsible for running commands.
	"""
	SV.cmd_queue.put(run_event)
	return



def get_event_from_the_command_queue():
	event = SV.cmd_queue.get() # blocking
	logger.debug(f"getting event from the command queue")
	return event

def send_sentinel_to_output_listener_thread():
	SV.out_queue.put('Done')


def termination_process(thread_pool):
	"""
 	handles the termination process of this thread.
  	Shutdoesn the thread pool that was executing commands
   	"""
	logger.info("Finishing...")
	logger.info("shutting down the pool")

	thread_pool.shutdown(wait=True) # shutdown the pool
	send_sentinel_to_output_listener_thread() # shutdown message to output parser

	logger.info("sending 'Done' to output")
	return


def run_command_in_another_process(cmd):
	logger.debug(f"[Pool thread]: calling Popen for command: {cmd}")
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
	return proc


def store_the_pid_of_process_in_pids_executing_commands(cmd, pid):
	try: 
		logger.debug(f"[Pool thread {cmd}]: storing PID: {pid}")

		SV.add_pid_to_cmd_pid_dict(cmd, pid)
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
		SV.del_pid_from_cmd_pid_dict(cmd, pid)
	except SE.CommandNotBeingRun as e:
		raise Exception(f"Command {cmd} was not being run")


def write_output_of_command_to_its_respective_file(out_file, pid, output):
	try:
		logger.debug(f"[Pool thread {pid}] writting to file: {out_file}")
		with open(out_file, 'w') as file:
			file.write(output)
		return
	except FileNotFoundError as e:
		raise Exception("File Not Found")

def create_event_for_output_listener(cmd, output, returncode, method, context):
	event = Done_Event('done', cmd, output, returncode, method, context)
	logger.debug(f"Created event successfully")
	return event

def send_event_for_output_parsing(done_event):
	"""
	sends the event to the outputs queue
	"""
	SV.out_queue.put(done_event)
	logger.debug(f"[Pool thread {done_event.command}] sended Done Event to outputs")


def thread_pool_run_normal_command(out_file:str, cmd:str, method:AbstractMethod, context:dict):
	SV.add_command_to_list_of_commands_run(cmd)
	# maybe do the check here? 
	proc = run_command_in_another_process(cmd)
	store_the_pid_of_process_in_pids_executing_commands(cmd, proc.pid)
	proc_stdout, proc_stderr = wait_for_process_to_complete_and_get_output_and_err(proc)
	remove_the_pid_of_process_from_the_pids_executing_commands(cmd, proc.pid)
	# know what to send to filter
	output = proc_stdout if proc.returncode == 0 else proc_stderr
	write_output_of_command_to_its_respective_file(out_file, proc.pid, output)

	event = create_event_for_output_listener(cmd, output, proc.returncode, method, context)
	send_event_for_output_parsing(event)
	return


def submit_new_cmd_to_thread_pool(thread_pool, out_file, cmd, method, context):
	thread_pool.submit(thread_pool_run_normal_command, out_file, cmd, method, context)
	logger.debug(f" submitted to the thread pool: {cmd}")


def handle_normal_command(thread_pool, out_file, cmd, method, context):
	if not SV.know_if_commands_was_already_run(cmd):
		SV.add_command_to_commands_for_analysis(cmd)
		submit_new_cmd_to_thread_pool(thread_pool, out_file, cmd, method, context)
	else:
		logger.warning(f" {cmd} was already run!!")



def call_methods_of_updated_objects():
	"""
	Calls the auto functions for the updated objects
	"""
	# copy the list so we don't end up updating it as well 
	with SV.shared_lock:
		logger.debug(f"Calling auto_function of the updated objects")
		updated_objects = copy.deepcopy(SV.updated_objects) 
		for component in updated_objects:
			component.auto_function()
		SV.clear_set_of_updated_objects()
	return



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
			# IF THIS IS TOO SLOW; PUT THIS PROCESS OF CALL METHODS IN ANOTHER THREAD
			# THIS WAY WE CAN RECEIVE COMMANDS WHILE WE PROCESS IT
			# if there is no command for analysis and no command to be read from the queue -> finish
			if SV.cmd_queue.empty() and SV.check_if_there_are_no_commands_for_analysis():
				logger.debug(f"Checking if there were updated objects")
				# empty = kill
				if SV.is_set_of_updated_objects_empty():
					termination_process(thread_pool)
					break # end of thread 
				call_methods_of_updated_objects()
				SV.cmd_queue.put('Done')
				
		
		else:
			# event must be of type run
			if event.type != 'run':
				logger.warning(f"run commands thread received a non RUN event")
				# nothing to do with that event
				SV.cmd_queue.task_done()

			# know the events attributes
			out_file, cmd, method, context = event.get_attributes()
			handle_normal_command(thread_pool, out_file, cmd, method, context)

			# signal task done
			SV.cmd_queue.task_done()
	
	#SV.cmd_queue.join() # every command inserted
	return