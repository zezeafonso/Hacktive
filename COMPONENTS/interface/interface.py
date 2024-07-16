from LOGGER.loggerconfig import logger

import THREADS.sharedvariables as SV
from THREADS.sharedvariables import shared_lock
from THREADS.runcommandsthread import send_run_event_to_run_commands_thread

from COMPONENTS.abstract.abstractnetworkcomponent import AbstractNetworkComponent
from COMPONENTS.network.network import Network



class Interface(AbstractNetworkComponent):
	"""
	add: 
	- dhcp broadcast discover 
	- responder analyzer (more on this later)
	"""
	methods = {}

	def __init__(self, interface_name:str, path:dict):
		self.interface_name = interface_name
		self.networks = {}
		self.path = path.copy()
		self.path['interface'] = self

		self.state = None # Corresponds to the (present) context)
		# the list of objects that depend on the state of this one
		# No one depends on the interface
		self.dependent_objects = list() 

		# will call the automatic methods
		self.check_for_updates_in_state()

	def get_context(self):
		"""
		Defines the context in which the methods will be called
		"""
		with shared_lock:
			logger.debug(f"getting context for Interface ({self.interface_name})")
			context = dict()
			context['interface_name'] = self.get_interface_name()
			return context 

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with shared_lock:
			new_state = self.get_context()
			# first run: context != None
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 



	def display_json(self):
		with shared_lock:
			data = dict()
			data['interface'] = dict()
			data['interface']['name'] = self.interface_name
			data['interface']['networks'] = list()
			for network_name in self.networks:
				data['interface']['networks'].append(self.networks[network_name].display_json())
			return data

	def add_network(self, network:Network):
		# TODO: check if already exists
		self.networks[network.network_address] = network


	# LOCK
	def attach_network(self, network_name:str):
		with shared_lock:
			if network_name in self.networks:
				pass
			else:
				print(f"creating new network: {network_name}")
				new_network = Network(network_name, self.path)
				self.networks[network_name] = new_network
				return new_network

	# please use a LOCK
	def check_for_network_str(self, network_name:str):
		"""
		if network exists, return the object
		"""
		with shared_lock:
			if network_name in self.networks:
				return self.networks[network_name]
		return None

	def create_network_with_network_str(self, network_name:str):
		"""
		creates the network; attaches it to the interface obj;
		returns the list of methods to run
		"""
		with shared_lock:
			new_network = Network(network_name, self.path) 
			self.networks[network_name] = new_network

			# because we updated this object -> check for relevance
			self.check_for_updates_in_state()
			return new_network

	def get_network_or_create_it(self, network_str):
		"""
		USER INPUT - must choose if we want to add new network

		retrieves the network object with network_str, if 
		it exists for this interface. Otherwise, creates a new 
		object network.

		If the network didn't exist. We will ask the user if 
		he wants to keep it as a network component

		returns: dict with 'object' and 'methods' (if we created a 
		new network obj)
		"""
		# if network doesn't exist create it and get methods
		with shared_lock:
			network = self.check_for_network_str(network_str)
			if network == None: # doesn't exist
				# create the network, but first ask if we want it 
				choice = input(f"[I]: add network ({network_str})? (y/n)")
				# ASK THE USER IF THIS NETWORK IS THE ONE
				if choice == 'yes' or choice == 'y':
					# checks for updates as well
					network = self.create_network_with_network_str(network_str)
					return network
				else:
					return None
			else: # it exists
				return network

	def found_network_methods(self, network:Network):
		"""
		the methods that we'll run when we find a network
		MUST RETURN A LIST
		"""
		return [network.auto]

	def get_network(self, network_name:str):
		if network_name not in self.networks:
			return None
		return self.networks[network_name]

	"""
	Run this when we find a new interface
	"""
	def auto_function(self):
		# no need for lock, the methods don't change
		for method in self.methods:
			list_events = method.create_run_events(self.state)
			for event in list_events:
				send_run_event_to_run_commands_thread(event)

	def display(self):
		print(f"Interface: {self.interface_name}")
		display_str = "networks:\n"
		for network_address in self.networks:
			display_str += " - "+self.networks[network_address].to_str() + '\n'
			display_str += "methods:"
		for method in self.__class__.methods:
			continue
		print(display_str)

	def get_root(self):
		return self.path['root']

	def get_interface(self):
		return self.path['interface']

	def get_interface_name(self):
		return self.interface_name
