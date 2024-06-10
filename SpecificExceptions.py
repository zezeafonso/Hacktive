class LockNotInit(Exception):
	pass

class NoUpdateComponentForThatClass(Exception):
	pass

class CommandAlreadyBeingRun(Exception):
	pass

class CommandNotBeingRun(Exception):
	pass

class CommandsListenerReceivedNonRunEvent(Exception):
	pass