import pygame
import pypboy
import config

from pypboy.modules.data import entities


class Module(pypboy.SubModule):
    label = "World Map"
    zoom = 0.1  # World map starts at wider zoom level

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        self.dragging = False  # Track drag state for touch/mouse panning
        self.mapgrid = entities.Map(480, pygame.Rect(0, 0, config.WIDTH - 8, config.HEIGHT - 80))
        self.mapgrid.fetch_map(config.MAP_FOCUS, self.zoom)
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
        """Handle zoom actions."""
        if action == "zoom_in":
            self.zoom = max(0.01, self.zoom - 0.01)  # Prevent negative zoom
            print(f"World map zoom: {self.zoom}")
            self.mapgrid.fetch_map(config.MAP_FOCUS, self.zoom)
        elif action == "zoom_out":
            self.zoom = min(1.0, self.zoom + 0.01)  # Cap maximum zoom out
            print(f"World map zoom: {self.zoom}")
            self.mapgrid.fetch_map(config.MAP_FOCUS, self.zoom)
        elif action in self.action_handlers:
            self.action_handlers[action]()

    def handle_resume(self):
        self.parent.pypboy.header.headline = "DATA"
        self.parent.pypboy.header.title = ["World Map"]
        super(Module, self).handle_resume()
