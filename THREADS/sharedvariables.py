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

"""
The root obj that is the root of the components in our application. 
In some, multiple, places in our code we need to access so we make 
it, global in this module.
Whenever you need it, just import this module and use it.
"""



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
	shared_lock = threading.RLock() # this way you can request the lock multiple times

	commands_for_analysis_list = list() # use with locks in threads
	commands_run_set = set()
 
 
def initialize_root_obj(obj) -> None:
    global root_obj
    
    root_obj = obj
    return 



def add_pid_to_cmd_pid_dict(cmd:str, pid:int, lock:threading.Lock) -> None:
	global cmd_pid_dict

	if cmd in cmd_pid_dict:
		raise CE.CommandAlreadyBeingRun(f"command: {cmd}, already in shared_dict!")
	cmd_pid_dict[cmd] = pid
	logger.debug(f"added pid {pid} to cmd_pid")


def del_pid_from_cmd_pid_dict(cmd:str, pid:int, lock:threading.Lock):
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






