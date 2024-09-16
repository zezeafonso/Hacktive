import threading
import queue

import EXCEPTIONS.commandexceptions as CE
from LOGGER.loggerconfig import logger


"""
The shared lock is necessary because multiple threads will 
try to access shared resources at the same time, for example
the methods or attributes that a network component might have
might be accessed in the same type that these components
are being updated with more.
"""
shared_lock = None


"""
The Objects that were updated since the last time we checked for the updated objects.
It's a set so we don't end up duplicating objects inside of it.
The purpose is that when we run out of commands we check to see if 
there were updated objects from the previous commands. 
If there were we check if these updates result in new commands for us
"""
updated_objects = None


"""
At all times we should know what processID is running what command.
When that process finishes, we have to take this command from the
dictionary.

TODO: when you take the command from the dictionary place it into 
a list of commands that were already run, this way we can always 
check if we already ran a specific command previously
"""
cmd_pid_dict = None

"""
The queue that we use to pass 'RUN' events, it's called commands queue
for me to remember that I know that this queue is the one being used 
to issue the events where the commands are present
"""
cmd_queue = None

"""
The queue that we use to pass 'DONE' events, it's called outputs queue 
for me to remember that I know that this queue is the one being used to
issue the events where the outputs are present 
"""
out_queue = None 

"""
The root obj that is the root of the components in our application. 
In some, multiple, places in our code we need to access so we make 
it, global in this module.
Whenever you need it, just import this module and use it.
"""
root_obj = None


def initialize():
	global out_queue
	global cmd_queue
	global cmd_pid_dict
	global shared_lock
	global commands_for_analysis_list
	global commands_run_set	
	global updated_objects

	out_queue = queue.Queue() # the queue for the parse outputs thread
	cmd_queue = queue.Queue() # the queue for the run commands thread
	cmd_pid_dict = dict() 
	shared_lock = threading.RLock() # lock for threads (re-entring)
	updated_objects = set() # the set of updated objects

	commands_for_analysis_list = list() # use with locks in threads
	commands_run_set = set() # commands that were run 
 
 
def initialize_root_obj(obj) -> None:
	global root_obj
	
	root_obj = obj
	return 



def add_pid_to_cmd_pid_dict(cmd:str, pid:int) -> None:
	global cmd_pid_dict

	if cmd in cmd_pid_dict:
		raise CE.CommandAlreadyBeingRun(f"command: {cmd}, already in shared_dict!")
	cmd_pid_dict[cmd] = pid
	logger.debug(f"added pid {pid} to cmd_pid")


def del_pid_from_cmd_pid_dict(cmd:str, pid:int):
	global cmd_pid_dict

	if cmd not in cmd_pid_dict:
		raise CE.CommandNotBeingRun(f"command: {cmd}, not being run")
	cmd_pid_dict.pop(cmd)
	logger.debug(f"removed {pid} from cmd_pid")


def know_if_commands_was_already_run(cmd):
	"""
	Checks if the command was already run.
	"""
	global commands_run_set
	global shared_lock

	with shared_lock:
		logger.debug(f" knowing if command {cmd} was already run")
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
		logger.debug(f" adding command for analysis")
		commands_for_analysis_list.append(cmd)


def remove_command_from_commands_to_analyze(cmd):
	global commands_for_analysis_list
	global shared_lock

	with shared_lock:
		logger.debug(f" removing {cmd} from the commands to analyze")
		for command in commands_for_analysis_list:
			if command == cmd:
				commands_for_analysis_list.remove(cmd)
				return 
		logger.warning(f" ({cmd}) wasn't present in the commands to be analyzed")


def check_if_there_are_no_commands_for_analysis():
	global commands_for_analysis_list
	global shared_lock

	with shared_lock:
		logger.debug(f" checking if there are still commands to analyze")
		if len(commands_for_analysis_list) == 0:
			res = True
		else:
			res = False
	return res


def add_object_to_set_of_updated_objects(obj):
	"""
	Adds an object to the set of updated objects
	"""
	global updated_objects
	with shared_lock:
		logger.debug(f"Adding object ({obj}) to set of updated objects")
		updated_objects.add(obj)
		return 


def clear_set_of_updated_objects():
	"""
	Clears the set of updated objects for a new cycle of commands
	"""
	global updated_objects
	with shared_lock:
		logger.debug(f"Clearing set of updated objects")
		updated_objects.clear()
		return 
	

def is_set_of_updated_objects_empty():
	"""
	Checks if there are objects inside the updated objects set
	"""
	with shared_lock:
		if len(updated_objects) == 0:
			return True
		return False





