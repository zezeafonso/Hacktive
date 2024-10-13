"""
This technique is associated to the DNS server, because you should 
only do a zone transfer for the domain that the DNS server is authorative for. 

The name of the domain, this DNS server belongs to is accessible from the DNS server"""


from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.abstract.abstractmethod import AbstractMethod

from THREADS.events import Run_Event
import THREADS.sharedvariables as sharedvariables

from COMPONENTS.dns.zonetransfer.filter import ZoneTransfer_Filter
from COMPONENTS.dns.zonetransfer.updater import update_zone_transfer
from LOGGER.loggerconfig import logger


class ZoneTransfer(AbstractMethod):
	"""
	Emumera the users that belong to a group through rpc 
	You will need the group name, and the ip of the msrpc server
	"""
	_name = 'DNS zone transfer'
	_filename = 'outputs/dns-zone-transfer'
	_previous_args = set()
	_filter = ZoneTransfer_Filter
	_updater = update_zone_transfer

	def __init__(self):
		pass

	@staticmethod
	def to_str():
		return f"{ZoneTransfer._name}"

	@staticmethod
	def create_run_events(context:dict=None) -> list:
		
		if context is None:
			logger.debug(f"Zone transfer didn't receive any context")
			return []

		if not ZoneTransfer.check_context(context):
			return []

		with sharedvariables.shared_lock:
			# extract the specific variables for this command
			dns_server = context['ip']
			domain_name = context['domain_name']
   
			unused_args = list()
			tup_args = (dns_server, domain_name)
			if not ZoneTransfer.check_if_args_were_already_used(tup_args):
				unused_args.append(tup_args)
				ZoneTransfer._previous_args.add(tup_args)

		# command to run 
		list_run_events = list()
  
		# for every unused msrpc server ip 
		for tup in unused_args:
			ip = tup[0]
			domain_name = tup[1] # in hex
			cmd = f"dig axfr {domain_name} @{ip}"

			# output file 
			str_ip_address = ip.replace('.', '_')
			output_file = ZoneTransfer._filename + str_ip_address +'-'+str(domain_name)+'.out'
			list_run_events.append(Run_Event( \
                    type='run', \
                    filename='outputs/'+cmd+'.out', \
                    command=cmd, \
                    method=ZoneTransfer, \
                    context=context))
   
		return list_run_events

	@staticmethod
	def check_for_objective(context):
		"""
		checks if the purpose of this method was already fullfilled.

		returns True if we should run it 
		"""
		return True

	@staticmethod
	def check_context(context:dict):
		"""
		Checks if the context provided to run the method has the
		necessary values
		"""
		if context['ip'] is None :
			logger.debug(f"context for ZoneTransfer doesn't have DNS servers")
			return False
		if context['domain_name'] is None:
			logger.debug(f"context for ZoneTransfer doesn't have a domain name")
			return False
		return True

	@staticmethod
	def check_if_args_were_already_used(arg:tuple):
		"""
		Checks if the args were already used, if so don't create 
		the run events
		MUST BE USED WITH A LOCK
		"""
		if arg in ZoneTransfer._previous_args:
			logger.debug(f"arg for ZoneTransfer was already used ({arg})")
			return True 
		return False 