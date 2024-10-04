import threading
from concurrent.futures import ThreadPoolExecutor
import json

from COMPONENTS.root.root import Root
from THREADS.runcommandsthread import commands_listener
from THREADS.parseoutputsthread import outputs_listener
import THREADS.sharedvariables as sharedvariables
from LOGGER.loggerconfig import logger


import input_json as IJ
import output_json as OJ


def main():
	# initialize the shared objects 
	sharedvariables.initialize()
	
	# initialize the json methods configuration
	methods_json = IJ.read_config_methods() 
	sharedvariables.initialize_methods_list(methods_json)

	# the thread pool executor for running commands
	thread_pool = ThreadPoolExecutor(max_workers=3)
	
	root = Root() # the root of the user interaction
	sharedvariables.initialize_root_obj(root) # to keep the object accessible
 
	# listener Thread for event 'run', Daemons to get killed when main dies
	commands_thread = threading.Thread(target=commands_listener, args=(thread_pool,), daemon=True)
	commands_thread.start()

	# listener thread for event 'done', Daemons to get killed when main dies
	outputs_thread = threading.Thread(target=outputs_listener, args=(), daemon=True) # TODO 
	outputs_thread.start()

	# Thread for handling user input Daemon
	start_issuing_commands_thread = threading.Thread(target=root.auto_function, args=())
	start_issuing_commands_thread.start()

	# Wait for user input thread to finish
	start_issuing_commands_thread.join()

	commands_thread.join()
	outputs_thread.join()


	# visualize the data in a file
	OJ.write_to_file('final.json', root)
	
	print("\n[!] END: all threads done")
	exit()

	

if __name__ == "__main__":
	main()