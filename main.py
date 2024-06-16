import threading
import queue
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import logging
import json


from NetworkComponents import Root
import NetworkComponentUpdater as NCU
import EventDoneThread as EDT
import CommandsListener as CL
import LoggingConfig
import ThreadShares
from LoggingConfig import logger
import output_json as OJ


def main():
	# initialize the shared objects 
	ThreadShares.initialize()

	# the thread pool executor for running commands
	thread_pool = ThreadPoolExecutor(max_workers=3)
	
	# TODO: this will be global, in order for us to manipulate it
	root = Root() # the root of the user interaction

	NCU.init_root_object(root)
	
	# Start the user input process
	#input_process = multiprocessing.Process(target=blocking_input, args=(input_queue, stop_event))
	#input_process.start()

	# listener Thread for event 'run', Daemons to get killed when main dies
	event_run_thread = threading.Thread(target=CL.commands_listener, args=(thread_pool,), daemon=True)
	event_run_thread.start()

	# listener thread for event 'done', Daemons to get killed when main dies
	event_done_thread = threading.Thread(target=EDT.outputs_listener, args=(root,), daemon=True) # TODO 
	event_done_thread.start()

	# Thread for handling user input Daemon
	# TODO: send shared lock as well 
	#user_interaction_thread = threading.Thread(target=root.user_interaction, args=(commands_queue, shared_lock, input_queue, stop_event, "console >"))
	user_interaction_thread = threading.Thread(target=root.auto, args=("console >",))
	user_interaction_thread.start()

	# Wait for user input thread to finish
	user_interaction_thread.join()
	logger.info("[Main]: user interaction thread finished")
	event_run_thread.join()
	event_done_thread.join()


	# visualize the data in a file
	OJ.write_to_file('final.json', root)
	
	print("All threads done")
	exit()

	

if __name__ == "__main__":
	main()