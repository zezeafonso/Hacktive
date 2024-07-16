from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as SV
from THREADS.sharedvariables import shared_lock
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.interface.interface import Interface
from COMPONENTS.domains.domain import Domain
from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent

from COMPONENTS.root.listinterfaces.method import ListInterfaces


class Root():
	"""
	The methods to be run should come from a file not hardcoded.
	"""
	methods = {ListInterfaces._name: ListInterfaces}

	def __init__(self):
		self.interfaces = {}
		self.path = {'root':self} # the path to this object
		self.domains = list() # empty list for the domains we find

		# this will be the current state of the context 
		# for now is None, because we haven't once checked for it.
		self.state = None 
		# the objects that depend on the root for context
		self.dependent_objects = list()

	# getters

	def get_context(self):
		logger.debug(f"getting context for Root")
		return dict

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 


	def get_root(self):
		return self.path['root']

	# Functions
	def auto_function(self, banner:str = 'console >'):
		"""
		Calls each method that is present in the list of methods with the 
		current state of the object.
		"""
		# no need for lock, the methods don't change
		for method in self.methods:
			list_events = self.methods[method].create_run_events(self.get_context())
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def display_json(self):
		with shared_lock:
			data = dict()
			data['interfaces'] = list()
			for _int in self.interfaces:
				interface = self.interfaces[_int]
				data['interfaces'].append(interface.display_json())
				#data['interface'] = interface.display_json()
			data['domains'] = list()
			for domain in self.domains:
				data['domains'].append(domain.display_json())
			return data

	def add_interface(self, interface:Interface):
		# call the methods from the interface
		self.interfaces[interface.interface_name] = interface

	def get_domains(self) -> list:
		with shared_lock:
			return self.domains

	# LOCK.
	# if new object return it 
	def attach_interface(self, interface_name:str):
		with shared_lock:
			if interface_name in self.interfaces:
				pass
			else:
				print(f"creating new interface: {interface_name}")
				new_interface = Interface(interface_name, self.path)
				self.interfaces[interface_name] = new_interface
				return new_interface

	def get_interface(self, interface_name:str):
		if interface_name not in self.interfaces:
			return None
		return self.interfaces[interface_name]


	# please use a LOCK
	def check_for_interface_name(self, interface_name:str):
		"""
		if interface exists, return the object
		"""
		if interface_name in self.interfaces:
			return self.interfaces[interface_name]
		return None


	def create_interface_with_name(self, interface_name:str):
		"""
		creates the interface; attaches it to the root obj;
		returns the list of methods to run
		"""
		new_interface = Interface(interface_name, self.path)
		self.interfaces[interface_name] = new_interface

		# because we updated the object -> check for relevance
		self.check_for_updates_in_state()
		return new_interface


	def get_interface_or_create_it(self, interface_name:str):
		"""
		Retrieves the existing interface, if it exists, or 
		creates a new one.

		returns a dictionary with 'object' and 'methods' (in case
		of new interface)
		"""
		# if interface doesn't exist create it and get methods
		with shared_lock:
			interface = self.check_for_interface_name(interface_name)
			if interface is None: # doesn't exist
				interface = self.create_interface_with_name(interface_name)
				return interface
			else:
				return interface # the correct interface object


	def check_for_domain(self, domain_name):
		with shared_lock:
			logger.debug("checking if domain ({domain.get_domain_name()}) is present in root")
			for domain in self.domains:
				if domain.get_domain_name() == domain_name:
					logger.debug(f"domain ({domain.get_domain_name()}) is present")
					return domain
			logger.debug(f"domain ({domain_name}) is NOT present")
			return None

	def add_domain(self, domain:Domain):
		with shared_lock:
			logger.debug(f"Adding domain ({domain.get_domain_name()}) to root")
			self.domains.append(domain)

	def get_or_create_domain(self, domain_name):
		with shared_lock:
			# check if domain is there.
			domain = self.check_for_domain(domain_name)
			if domain is None:
				# create the Domain
				domain = Domain(domain_name=domain_name)
				# check if it belongs to some forest? 
				self.add_domain(domain)
			return domain
