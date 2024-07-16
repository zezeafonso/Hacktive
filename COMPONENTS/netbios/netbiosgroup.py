
class NetBIOSGroup():
	methods = [Methods.NBNSGroupMembers]

	def __init__(self, group_name, group_type):
		"""
		The type of the group clarifies if this is <00> or <1c>
		"""
		self.name = group_name
		self.type = group_type
		self.id = group_name.lower()+'#'+group_type
		self.associated = None # the object to which is associated (network / wins server)

		# the current context of the object
		self.state = None
		# the objects that depend on this object for context
		self.dependent_objects = list()

		self.check_for_updates_in_state()

	def get_id(self):
		with TS.shared_lock:
			return self.id

	def get_context(self):
		with TS.shared_lock:
			logger.debug(f"getting context for NetBIOSGroup ({self.name})")
			context = dict()
			context['group_name'] = self.name
			context['group_id'] = self.id
			context['associated_object'] = self.associated # might be None
		return context

	def check_for_updates_in_state(self):
		"""
		Checks for updates in the state of this interface.
		If so, calls for the state of the objects that depend on this.
		calls it's methods.
		"""
		with TS.shared_lock:
			new_state = self.get_context()
			if new_state != self.state:
				self.state = new_state

				# check for updates in dependent objects
				for obj in self.dependent_objects:
					obj.check_for_updates_in_state()
				
				# call for out methods
				self.auto_function()
			return 

	def display_json(self):
		with TS.shared_lock:
			data = dict()
			data['NetBIOSGroup'] = dict()
			data['NetBIOSGroup']['id'] = self.id
			return data

	def add_group_member(self):
		"""
		Function to add a group member to a netBIOS group
		this way we can also get the member through here
		"""
		pass

	def auto_function(self):
		"""
		Defines the functions that runs the automatic methods 
		for when we find a new netBIOS group.

		You should only do this, whenever you associate the group object 
		to another object, the methods here are for when you find a new
		netbios group. In our case the object must be associated with 
		the network or wins server so that the methods work.
		"""
		# I want for us to find the other bitches that belong to this one
		# TODO : add the method for nmblookup that finds the other ip's for this group
		list_events = []
		for method in self.methods:
			list_events += method.create_run_events(self, self.state)
			for event in list_events:
				throw_run_event_to_command_listener(event)

	def associate_with_object(self, obj):
		"""
		Associates this network group, with something, most likely 
		the network or subnet where we are present.
		"""
		if isinstance(obj, Network):
			with TS.shared_lock:
				if self.associated is not None:
					logger.debug(f"changing the associated object of netbios group ({self.id})")
				self.associated = obj

				self.check_for_updates_in_state()
				return

