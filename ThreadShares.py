import threading
import queue
import logging

import SpecificExceptions as SE
import LoggingConfig


"""
The shared lock is necessary because multiple threads will 
try to access shared resources at the same time, for example
the methods or attributes that a network component might have
might be accessed in the same type that these components
are being updated with more.
"""
global shared_lock

"""
At all times we should know what processID is running what command.
When that process finishes, we have to take this command from the
dictionary.

TODO: when you take the command from the dictionary place it into 
a list of commands that were already run, this way we can always 
check if we already ran a specific command previously
"""
global cmd_pid_dict

"""
The queue that we use to pass 'RUN' events, it's called commands queue
for me to remember that I know that this queue is the one being used 
to issue the events where the commands are present
"""
global cmd_queue

"""
The queue that we use to pass 'DONE' events, it's called outputs queue 
for me to remember that I know that this queue is the one being used to
issue the events where the outputs are present 
"""
global out_queue 



def initialize():
	global out_queue
	global cmd_queue
	global cmd_pid_dict
	global shared_lock
	global commands_for_analysis_list
	global commands_run_set	

	out_queue = queue.Queue()
	cmd_queue = queue.Queue()
	cmd_pid_dict = dict()
	shared_lock = threading.Lock()

	commands_for_analysis_list = list() # use with locks in threads
	commands_run_set = set()

	LoggingConfig.configure_logging()



def add_pid_to_cmd_pid_dict(cmd:str, pid:int, lock:threading.Lock) -> None:
	global cmd_pid_dict

	logging.info(f"[TS] adding pid {pid} to cmd_pid")
	if cmd in cmd_pid_dict:
		raise SE.CommandAlreadyBeingRun(f"command: {cmd}, already in shared_dict!")
	cmd_pid_dict[cmd] = pid
	logging.info(f"[TS] adding pid {pid} to cmd_pid: SUCCESS")


def del_pid_from_cmd_pid_dict(cmd:str, pid:int, lock:threading.Lock):
	global cmd_pid_dict

	logging.info(f"[TS] removing {pid} from cmd_pid")
	if cmd not in cmd_pid_dict:
		raise SE.CommandNotBeingRun(f"command: {cmd}, not being run")
	cmd_pid_dict.pop(cmd)
	logging.info(f"[TS] removing {pid} from cmd_pid: SUCCESS")


def know_if_commands_was_already_run(cmd):
	global commands_run_set
	global shared_lock

	with shared_lock:
		res = cmd in commands_run_set
	return res

def add_command_to_list_of_commands_run(cmd):
	global commands_run_set
	global shared_lock

	with shared_lock:
		commands_run_set.add(cmd)

def add_command_to_commands_for_analysis(cmd):
	global commands_for_analysis_list
	global shared_lock

	with shared_lock:
		commands_for_analysis_list.append(cmd)

def remove_command_from_commands_to_analyze(cmd):
	global commands_for_analysis_list
	global shared_lock

	with shared_lock:
		for command in commands_for_analysis_list:
			if command == cmd:
				commands_for_analysis_list.remove(cmd)

def check_if_there_are_no_commands_for_analysis():
	global commands_for_analysis_list
	global shared_lock

	with shared_lock:
		if len(commands_for_analysis_list) == 0:
			res = True
		else:
			res = False
	return res






