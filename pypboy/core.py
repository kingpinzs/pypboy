import pygame
import config
import game
import pypboy.ui

from pypboy.modules import data
from pypboy.modules import items
from pypboy.modules import stats

if config.GPIO_AVAILABLE:
    import RPi.GPIO as GPIO


class Pypboy(game.core.Engine):

    def __init__(self, *args, **kwargs):
        if hasattr(config, 'OUTPUT_WIDTH') and hasattr(config, 'OUTPUT_HEIGHT'):
            self.rescale = True
        super(Pypboy, self).__init__(*args, **kwargs)
        self.init_children()
        self.init_modules()
        
        self.gpio_actions = {}
        if config.GPIO_AVAILABLE:
            self.init_gpio_controls()

    def init_children(self):
        self.background = pygame.image.load('images/overlay.png')
        # border = pypboy.ui.Border()
        # self.root_children.add(border)
        # More subtle scanlines - reduced alpha/RGB values
        scanlines = pypboy.ui.Scanlines(800, 480, 3, 1, [(0, 4, 1, 12), (2, 12, 6, 25), (0, 4, 1, 12)])
        self.root_children.add(scanlines)
        scanlines2 = pypboy.ui.Scanlines(800, 480, 8, 40, [(0, 3, 0, 0), (6, 18, 12, 20), (18, 36, 24, 28), (6, 18, 12, 20)] + [(0, 3, 0, 0) for x in range(50)], True)
        self.root_children.add(scanlines2)
        self.header = pypboy.ui.Header()
        self.root_children.add(self.header)

    def init_modules(self):
        self.modules = {
            "data": data.Module(self),
            "items": items.Module(self),
            "stats": stats.Module(self)
        }
        for module in self.modules.values():
            module.move(4, 40)
        self.switch_module("stats")

    def init_gpio_controls(self):
        for pin in config.GPIO_ACTIONS.keys():
            print("Intialising pin %s as action '%s'" % (pin, config.GPIO_ACTIONS[pin]))
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.gpio_actions[pin] = config.GPIO_ACTIONS[pin]

    def check_gpio_input(self):
        for pin in self.gpio_actions.keys():
            if GPIO.input(pin) == False:
                self.handle_action(self.gpio_actions[pin])

    def update(self):
        if hasattr(self, 'active'):
            self.active.update()
        super(Pypboy, self).update()

    def render(self):
        interval = super(Pypboy, self).render()
        if hasattr(self, 'active'):
            self.active.render(interval)

    def switch_module(self, module):
        if module in self.modules:
            if hasattr(self, 'active'):
                self.active.handle_action("pause")
                self.remove(self.active)
            self.active = self.modules[module]
            self.active.parent = self
            self.active.handle_action("resume")
            self.add(self.active)
        else:
            print("Module '%s' not implemented." % module)

    def handle_action(self, action):
        if action.startswith('module_'):
            self.switch_module(action[7:])
        else:
            if hasattr(self, 'active'):
                self.active.handle_action(action)

    def handle_click(self, pos):
        """Route click/tap to active module for screen interactions."""
        x, y = pos

        # Ignore header region (y < 40)
        if y < 40:
            return

        # Ignore footer region (y > HEIGHT - 53) - tabs are button-controlled
        if y > config.HEIGHT - 53:
            return

        # Main content area - delegate to active module
        if hasattr(self, 'active') and self.active:
            self.active.handle_click(pos)

    def handle_click_release(self, pos):
        """Route click/tap release to active module."""
        if hasattr(self, 'active') and self.active:
            self.active.handle_click_release(pos)

    def handle_drag(self, pos, rel):
        """Route drag to active module (for map panning)."""
        if hasattr(self, 'active') and self.active:
            self.active.handle_drag(pos, rel)

    def handle_event(self, event):
        # Keyboard events - keep existing for module/submodule switching
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            else:
                if event.key in config.ACTIONS:
                    self.handle_action(config.ACTIONS[event.key])

        # Mouse events for desktop interaction
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click / touch
                self.handle_click(event.pos)
            elif event.button == 4:  # Scroll up - navigate menu
                self.handle_action("dial_up")
            elif event.button == 5:  # Scroll down - navigate menu
                self.handle_action("dial_down")

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.handle_click_release(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # Left button held - drag
                self.handle_drag(event.pos, event.rel)

        # SDL2 Touch/Finger events (for Pi touchscreen)
        elif event.type == pygame.FINGERDOWN:
            # Convert normalized coords (0.0-1.0) to pixels
            x = int(event.x * config.WIDTH)
            y = int(event.y * config.HEIGHT)
            self.handle_click((x, y))

        elif event.type == pygame.FINGERUP:
            x = int(event.x * config.WIDTH)
            y = int(event.y * config.HEIGHT)
            self.handle_click_release((x, y))

        elif event.type == pygame.FINGERMOTION:
            x = int(event.x * config.WIDTH)
            y = int(event.y * config.HEIGHT)
            # dx/dy are also normalized, convert to pixel delta
            rel_x = int(event.dx * config.WIDTH)
            rel_y = int(event.dy * config.HEIGHT)
            self.handle_drag((x, y), (rel_x, rel_y))

        elif event.type == pygame.QUIT:
            self.running = False

        elif event.type == config.EVENTS['SONG_END']:
            if config.SOUND_ENABLED:
                if hasattr(config, 'radio'):
                    config.radio.handle_event(event)

        else:
            if hasattr(self, 'active'):
                self.active.handle_event(event)

    def run(self):
        self.running = True
        while self.running:
            self.check_gpio_input()
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.render()
            pygame.time.wait(1)

        try:
            pygame.mixer.quit()
        except:
            pass
