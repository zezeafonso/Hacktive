from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables


from LOGGER.loggerconfig import logger
from COMPONENTS.hosts.portscan.filter import PortScan_Filter
from COMPONENTS.hosts.portscan.updater import updater

class PortScan(AbstractMethod):
	_name = 'port scan'
	_filename = 'outputs/port_scan'
	_filter = PortScan_Filter
	_updater = updater

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{PortScan._name}"

	@staticmethod
	def create_run_events(nc:AbstractNetworkComponent) -> list:
		"""
		nc should be a Network (component) for us to be able
		to get the network address.
		"""
		# obter o ip do host
		_ip = nc.get_ip()
		if _ip == None:
			return []

		# obter o output file com o ip do host
		str_ip = str(_ip).replace('.','_')
		output_file = PortScan._filename +str_ip + '.out'
		# chamar o comando para listar os portos
		cmd = f"sudo nmap -sS -n -Pn {_ip}"
		# criar o evento de run com o comando
		return [Run_Event(type='run', filename=cmd+'.out', command=cmd, method=PortScan, nc=nc)]

	@staticmethod
	def check_for_objective(nc):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True
