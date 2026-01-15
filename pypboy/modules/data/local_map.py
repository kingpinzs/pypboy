import pygame
import pypboy
import config

from pypboy.modules.data import entities

class Module(pypboy.SubModule):
    label = "Local Map"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        self.dragging = False  # Track drag state for touch/mouse panning

        # Create map with display rect
        display_rect = pygame.Rect(0, 0, config.WIDTH - 8, config.HEIGHT - 80)

        self.mapgrid = entities.Map(config.WIDTH, display_rect, "Loading map...")
        if config.LOAD_CACHED_MAP:
            self.mapgrid.load_map(config.MAP_FOCUS, 0.003)
        else:
            self.mapgrid.fetch_map(config.MAP_FOCUS, 0.003)

        self.add(self.mapgrid)
        self.mapgrid.rect[0] = 4
        self.mapgrid.rect[1] = 40

    def handle_click(self, pos):
        """Start drag operation on map."""
        self.dragging = True

    def handle_click_release(self, pos):
        """End drag operation."""
        self.dragging = False

    def handle_drag(self, pos, rel):
        """Pan map based on drag movement."""
        # Only pan if dragging and map is not currently loading
        if self.dragging and hasattr(self, 'mapgrid'):
            # Check if map is loading (thread is still alive)
            is_loading = (hasattr(self.mapgrid, '_fetching') and
                         self.mapgrid._fetching and
                         self.mapgrid._fetching.is_alive())
            if not is_loading:
                self.mapgrid.move_map(-rel[0], -rel[1])

    def handle_action(self, action, value=0):
        if action == "zoom_in":
            self.mapgrid.zoom_in()  # Fast! Just scales surface
        elif action == "zoom_out":
            self.mapgrid.zoom_out()  # Fast! Just scales surface
        self.parent.pypboy.header.headline = "DATA"
        self.parent.pypboy.header.title = ["Santa Clarita"]
    
    def handle_resume(self):
        self.parent.pypboy.header.headline = "DATA"
        self.parent.pypboy.header.title = ["Santa Clarita"]
        super(Module, self).handle_resume()