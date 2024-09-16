from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event

from LOGGER.loggerconfig import logger
from COMPONENTS.root.listinterfaces.filter import ListInterfaces_Filter
from COMPONENTS.root.listinterfaces.updater import update_list_interfaces



class ListInterfaces(AbstractMethod):
	_name = "list interfaces"
	_filename = "outputs/ListInterfaces.out"
	_filter = ListInterfaces_Filter
	_updater = update_list_interfaces

	# doesn't need anything to run 
	def __init__(self):
		pass

	@staticmethod
	def to_str() -> str: 
		name = ListInterfaces._name
		return f"{name}"

	@staticmethod
	def create_run_events(context:dict) -> list:
		method_name = ListInterfaces._name
		output_file = ListInterfaces._filename

		# context can be empty dict, but not None
		if context is None:
			logger.debug(f"ListInterfaces didn't receive any context")
			return []

		cmd = "ip a"
		return [Run_Event(type='run', filename=output_file, command=cmd, method=ListInterfaces, context=context)]

	@staticmethod
	def check_for_objective(context):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True