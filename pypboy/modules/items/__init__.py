from pypboy import BaseModule
from pypboy.modules.items import weapons
from pypboy.modules.items import apparel
from pypboy.modules.items import aid
from pypboy.modules.items import misc
from pypboy.modules.items import ammo


class Module(BaseModule):

	label = "INV"
	GPIO_LED_ID = 21

	def __init__(self, *args, **kwargs):
		self.submodules = [
			weapons.Module(self),
			apparel.Module(self),
			aid.Module(self),
			misc.Module(self),
			ammo.Module(self)
		]
		super(Module, self).__init__(*args, **kwargs)

	def handle_resume(self):
		self.pypboy.header.headline = self.label
		self.pypboy.header.title = []
		self.pypboy.header.show_date = False  # INV doesn't show date/time
		self.active.handle_action("resume")
