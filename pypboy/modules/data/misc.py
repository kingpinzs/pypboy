import pypboy

class Module(pypboy.SubModule):

	label = "Misc"

	def handle_resume(self):
		self.parent.pypboy.header.headline = "DATA"
		self.parent.pypboy.header.title = [self.label]
		super(Module, self).handle_resume()
