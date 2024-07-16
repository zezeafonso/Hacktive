import threading
from concurrent.futures import ThreadPoolExecutor

from COMPONENTS.root.root import Root
from THREADS.runcommandsthread import commands_listener
from THREADS.parseoutputsthread import outputs_listener
import THREADS.sharedvariables as sharedvariables
from LOGGER.loggerconfig import logger

import output_json as OJ


def main():
	# initialize the shared objects 
	sharedvariables.initialize()

	# the thread pool executor for running commands
	thread_pool = ThreadPoolExecutor(max_workers=3)
	
	# TODO: this will be global, in order for us to manipulate it
	root = Root() # the root of the user interaction
	sharedvariables.initialize_root_obj(root) # to keep the object accessible
 
	#NCU.init_root_object(root) 
	#FU.init_root_object(root)

	# listener Thread for event 'run', Daemons to get killed when main dies
	commands_thread = threading.Thread(target=commands_listener, args=(thread_pool,), daemon=True)
	commands_thread.start()

	# listener thread for event 'done', Daemons to get killed when main dies
	outputs_thread = threading.Thread(target=outputs_listener, args=(root,), daemon=True) # TODO 
	outputs_thread.start()

	# Thread for handling user input Daemon
	# TODO: send shared lock as well 
	#user_interaction_thread = threading.Thread(target=root.user_interaction, args=(commands_queue, shared_lock, input_queue, stop_event, "console >"))
	start_issuing_commands_thread = threading.Thread(target=root.auto_function, args=())
	start_issuing_commands_thread.start()

	# Wait for user input thread to finish
	start_issuing_commands_thread.join()
	logger.info("[Main]: user interaction thread finished")
	commands_thread.join()
	outputs_thread.join()


	# visualize the data in a file
	OJ.write_to_file('final.json', root)
	
	print("All threads done")
	exit()

	

if __name__ == "__main__":
	main()