from abc import ABC, abstractmethod


class AbstractFilteredObject(ABC):
	@abstractmethod
	def captured(self):
		pass
