import pygame
import pypboy
import config

from pypboy.modules.data import entities

class Module(pypboy.SubModule):
    label = "Local Map"
    load_cached_map = False
    zoom = 0.003

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        self.dragging = False  # Track drag state for touch/mouse panning
        self.mapgrid = entities.Map(config.WIDTH, pygame.Rect(4, (config.WIDTH - config.HEIGHT) / 2, config.WIDTH - 8, config.HEIGHT - 80))
        if(config.LOAD_CACHED_MAP):
            print("Loading cached map")
            self.mapgrid = entities.Map(config.WIDTH, pygame.Rect(4, (config.WIDTH - config.HEIGHT) / 2, config.WIDTH - 8, config.HEIGHT - 80), "Loading cached map")
            map_data_location = 'map.cache'
            self.mapgrid.load_map(config.MAP_FOCUS, self.zoom)
        else:
            print("Loading map from the internet")
            self.mapgrid = entities.Map(config.WIDTH, pygame.Rect(4, (config.WIDTH - config.HEIGHT) / 2, config.WIDTH - 8, config.HEIGHT - 80), "Loading map from the internet")
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
        if action == "zoom_in":
            self.zoom = self.zoom - 0.003
            print(self.zoom)
        if action == "zoom_out":
            self.zoom = self.zoom + 0.003
            print(self.zoom)
        self.mapgrid.fetch_map(config.MAP_FOCUS, self.zoom)
        self.add(self.mapgrid)
        self.mapgrid.rect[0] = 4
        self.mapgrid.rect[1] = 40
        self.parent.pypboy.header.headline = "DATA"
        self.parent.pypboy.header.title = ["Santa Clarita"]
    
    def handle_resume(self):
        self.parent.pypboy.header.headline = "DATA"
        self.parent.pypboy.header.title = ["Santa Clarita"]
        super(Module, self).handle_resume()