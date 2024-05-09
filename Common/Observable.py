class Observable:
	def __init__(self):
		self._observers = []

	def subscribe(self, observer):
		if observer is None:
			return
		self._observers.append(observer)

	def unsubscribe(self, observer):
		self._observers.remove(observer)

	def notify(self, *args, **kwargs):
		for observer in self._observers:
			observer.update(*args, **kwargs)

