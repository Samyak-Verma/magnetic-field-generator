# adds spans that work in CLI output

class span(object):
	def blue(text):
		return f"\033[34m{text}\033[0m"

	def green(text):
		return f"\033[32m{text}\033[0m"

	def red(text):
		return f"\033[31m{text}\033[0m"