class TimeKeeper:
	def __init__(self):
		self.time_to_setup = 3
		self.time_estimate = 0

	def calculate_time_estimate(self, number_of_measurements, milliseconds_between_measurements):
		# takes ~3 seconds to setup, and 0.4 more seconds for the machines to report results.
		self.time_estimate = (number_of_measurements * (milliseconds_between_measurements / 1000)) + (0.4 * number_of_measurements)
		return self.get_time_estimate()

	def get_time_estimate(self, include_setup_time = True):
		return '{:.1f}'.format(self.time_estimate + (self.time_to_setup if include_setup_time else 0))