from pypboy import BaseModule
from pypboy.modules.stats import status
from pypboy.modules.stats import special
from pypboy.modules.stats import skills
from pypboy.modules.stats import perks
from pypboy.modules.stats import general


class Module(BaseModule):

    label = "STATS"
    GPIO_LED_ID = 30 #GPIO 22 #19

    def __init__(self, *args, **kwargs):
        self.submodules = [
            status.Module(self),
            special.Module(self),
            skills.Module(self),
            perks.Module(self),
            general.Module(self)
        ]
        super(Module, self).__init__(*args, **kwargs)
        
    def handle_resume(self):
        self.pypboy.header.headline = self.label
        self.pypboy.header.title = ["XP 819/1050", "AP 77/77", "HP 221/230", "LVL 3"]
        self.pypboy.header.show_date = False  # STATS doesn't show date/time
        self.active.handle_action("resume")
