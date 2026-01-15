import os
import game
import config
import pygame
import threading
import pypboy.data
import time
from random import choice


class Map(game.Entity):
    """
    Map entity with surface-based zoom (Fallout Pip-Boy style).
    Simplified version closer to original working code.
    """

    _mapper = None
    _size = 0
    _fetching = None
    _map_surface = None
    _render_rect = None
    _zoom_level = 1.0

    def __init__(self, width, render_rect=None, loading_type="Loading map...", *args, **kwargs):
        self._mapper = pypboy.data.Maps()
        self._size = width
        self._map_surface = pygame.Surface((width, width))
        self._render_rect = render_rect if render_rect else pygame.Rect(0, 0, width, width)
        self._zoom_level = config.MAP_ZOOM_DEFAULT
        self._data_loaded = False
        self._is_loading = False
        self._needs_display_update = False  # Flag for thread-safe display updates

        super(Map, self).__init__((width, width), *args, **kwargs)
        text = config.FONTS[14].render(loading_type, True, (95, 255, 177), (0, 0, 0))
        self.image.blit(text, (10, 10))

    def fetch_map(self, position, radius):
        if self._is_loading:
            return
        self._is_loading = True
        self._fetching = threading.Thread(target=self._internal_fetch_map, args=(position, radius))
        self._fetching.start()

    def _internal_fetch_map(self, position, radius):
        self._mapper.fetch_by_coordinate(position, radius)
        self._redraw_map()
        self._data_loaded = True
        self._is_loading = False

    def load_map(self, position, radius):
        if self._is_loading:
            return
        self._is_loading = True
        self._fetching = threading.Thread(target=self._internal_load_map, args=(position, radius))
        self._fetching.start()

    def _internal_load_map(self, position, radius):
        self._mapper.load_map_coordinates(position, radius)
        self._redraw_map()
        self._data_loaded = True
        self._is_loading = False

    def _redraw_map(self):
        """Render map data to _map_surface (called from background thread)."""
        self._map_surface.fill((0, 0, 0))

        # Draw all roads
        for way in self._mapper.transpose_ways((self._size, self._size), (self._size / 2, self._size / 2)):
            pygame.draw.lines(self._map_surface, (85, 251, 167), False, way, 2)

        # Draw all POIs
        for tag in self._mapper.transpose_tags((self._size, self._size), (self._size / 2, self._size / 2)):
            if len(tag) >= 4 and tag[3] in config.AMENITIES:
                image = config.AMENITIES[tag[3]]
                scaled_icon = pygame.transform.scale(image, (10, 10))
                self._map_surface.blit(scaled_icon, (int(tag[1]), int(tag[2])))
                text = config.FONTS[12].render(tag[0], True, (95, 255, 177), (0, 0, 0))
                self._map_surface.blit(text, (int(tag[1]) + 17, int(tag[2]) + 4))

        # Signal main thread to update display (thread-safe)
        self._needs_display_update = True

    def _apply_zoom(self):
        """Apply current zoom level to display."""
        if self._zoom_level == 1.0:
            # No zoom - just blit the render rect area
            self.image.fill((0, 0, 0))
            self.image.blit(self._map_surface, (0, 0), area=self._render_rect)
        else:
            # Scale the map surface
            scaled_size = int(self._size * self._zoom_level)
            scaled = pygame.transform.scale(self._map_surface, (scaled_size, scaled_size))

            # Calculate the viewport rect on scaled surface
            # Center the view
            scale_factor = self._zoom_level
            src_x = int(self._render_rect.x * scale_factor)
            src_y = int(self._render_rect.y * scale_factor)
            src_w = self._render_rect.width
            src_h = self._render_rect.height

            # Clamp to bounds
            src_x = max(0, min(src_x, scaled_size - src_w))
            src_y = max(0, min(src_y, scaled_size - src_h))

            self.image.fill((0, 0, 0))
            self.image.blit(scaled, (0, 0), area=pygame.Rect(src_x, src_y, src_w, src_h))

    def zoom_in(self):
        """Zoom in - fast, no data re-fetch."""
        new_zoom = min(config.MAP_ZOOM_MAX, self._zoom_level + config.MAP_ZOOM_STEP)
        if new_zoom != self._zoom_level:
            self._zoom_level = new_zoom
            if self._data_loaded:
                self._apply_zoom()
                self.dirty = 1
            print(f"Zoom: {self._zoom_level:.2f}")

    def zoom_out(self):
        """Zoom out - fast, no data re-fetch."""
        new_zoom = max(config.MAP_ZOOM_MIN, self._zoom_level - config.MAP_ZOOM_STEP)
        if new_zoom != self._zoom_level:
            self._zoom_level = new_zoom
            if self._data_loaded:
                self._apply_zoom()
                self.dirty = 1
            print(f"Zoom: {self._zoom_level:.2f}")

    def move_map(self, x, y):
        """Pan the map."""
        self._render_rect.move_ip(x, y)
        if self._data_loaded:
            self._apply_zoom()
            self.dirty = 1

    def update(self, *args, **kwargs):
        # Check if background thread finished rendering and needs display update
        if self._needs_display_update:
            self._needs_display_update = False
            self._apply_zoom()
        # Keep dirty=2 since screen is cleared each frame
        self.dirty = 2
        super(Map, self).update(*args, **kwargs)

class MapSquare(game.Entity):
    _mapper = None
    _size = 0
    _fetching = None
    _map_surface = None
    map_position = (0, 0)

    def __init__(self, size, map_position, parent, *args, **kwargs):
        self._mapper = pypboy.data.Maps()
        self._size = size
        self.parent = parent
        self._map_surface = pygame.Surface((size * 2, size * 2))
        self.map_position = map_position
        self.tags = {}
        super(MapSquare, self).__init__((size, size), *args, **kwargs)

    def fetch_map(self):
        self._fetching = threading.Thread(target=self._internal_fetch_map)
        self._fetching.start()

    def _internal_fetch_map(self):
        self._mapper.fetch_grid(self.map_position)
        self.redraw_map()
        self.parent.redraw_map()

    def redraw_map(self, coef=1):
        self._map_surface.fill((0, 0, 0))
        for way in self._mapper.transpose_ways((self._size, self._size), (self._size / 2, self._size / 2)):
            pygame.draw.lines(
                    self._map_surface,
                    (85, 251, 167),
                    False,
                    way,
                    1
            )
        for tag in self._mapper.transpose_tags((self._size, self._size), (self._size / 2, self._size / 2)):
            self.tags[tag[0]] = (tag[1] + self.position[0], tag[2] + self.position[1], tag[3])
        self.image.fill((0, 0, 0))
        self.image.blit(self._map_surface, (-self._size / 2, -self._size / 2))

class MapGrid(game.Entity):

    _grid = None
    _delta = 0.002
    _starting_position = (0, 0)

    def __init__(self, starting_position, dimensions, *args, **kwargs):
        self._grid = []
        self._starting_position = starting_position
        self.dimensions = dimensions
        self._tag_surface = pygame.Surface(dimensions)
        super(MapGrid, self).__init__(dimensions, *args, **kwargs)
        self.tags = {}
        self.fetch_outwards()

    def test_fetch(self):
        for x in range(10):
            for y in range(5):
                square = MapSquare(
                    100,
                    (
                        self._starting_position[0] + (self._delta * x),
                        self._starting_position[1] - (self._delta * y)
                    )
                )
                square.fetch_map()
                square.position = (100 * x, 100 * y)
                self._grid.append(square)

    def fetch_outwards(self):
        for x in range(-4, 4):
            for y in range(-2, 2):
                square = MapSquare(
                    86,
                    (
                        self._starting_position[0] + (self._delta * x),
                        self._starting_position[1] - (self._delta * y)
                    ),
                    self
                )
                square.fetch_map()
                square.position = ((86 * x) + (self.dimensions[0] / 2) - 43, (86 * y) + (self.dimensions[1] / 2) - 43)
                self._grid.append(square)


    def draw_tags(self):
        self.tags = {}
        for square in self._grid:
            self.tags.update(square.tags)
        self._tag_surface.fill((0, 0, 0))
        for name in self.tags:
            if self.tags[name][2] in config.AMENITIES:
                image = config.AMENITIES[self.tags[name][2]]
            #else:
            #	print "Unknown amenity: %s" % self.tags[name][2]
            #	image = config.MAP_ICONS['misc']
                pygame.transform.scale(image, (10, 10))
                self.image.blit(image, (self.tags[name][0], self.tags[name][1]))
            # try:
                text = config.FONTS[12].render(name, True, (95, 255, 177), (0, 0, 0))
            # text_width = text.get_size()[0]
            # 	pygame.draw.rect(
            # 		self,
            # 		(0, 0, 0),
            # 		(self.tags[name][0], self.tags[name][1], text_width + 4, 15),
            # 		0
            # 	)
                self.image.blit(text, (self.tags[name][0] + 17, self.tags[name][1] + 4))
            # 	pygame.draw.rect(
            # 		self,
            # 		(95, 255, 177),
            # 		(self.tags[name][0], self.tags[name][1], text_width + 4, 15),
            # 		1
            # 	)
            # except Exception, e:
            # 	print(e)
            # 	pass

    def redraw_map(self, *args, **kwargs):
        self.image.fill((0, 0, 0))
        for square in self._grid:
            self.image.blit(square._map_surface, square.position)
        self.draw_tags()

class RadioStation(game.Entity):

    STATES = {
        'stopped': 0,
        'playing': 1,
        'paused': 2
    }

    def __init__(self, *args, **kwargs):
        super(RadioStation, self).__init__((10, 10), *args, **kwargs)
        self.state = self.STATES['stopped']
        self.files = self.load_files()
        pygame.mixer.music.set_endevent(config.EVENTS['SONG_END'])


    def play_random(self):
        start_pos = 0
        f = False
        if config.SOUND_ENABLED:
            if hasattr(self, 'last_filename') and self.last_filename:
                pygame.mixer.music.load(self.last_filename)

                now = time.time()
                curpos = self.last_playpos + (now - self.last_playtime)
                # TODO
            f = choice(self.files)
            self.filename = f
            pygame.mixer.music.load(f)
            pygame.mixer.music.play(0, start_pos)
            self.state = self.STATES['playing']
        
    def play(self):
        if config.SOUND_ENABLED:
            if self.state == self.STATES['paused']:
                pygame.mixer.music.unpause()
                self.state = self.STATES['playing']
            else:
                self.play_random()
        
    def pause(self):
        if config.SOUND_ENABLED:
            self.state = self.STATES['paused']
            pygame.mixer.music.pause()
        
    def stop(self):
        if config.SOUND_ENABLED:
            self.state = self.STATES['stopped']
            if self.filename:
                self.last_filename = self.filename
                self.last_playpos = pygame.mixer.music.get_pos()
                self.last_playtime = time.time()
            pygame.mixer.music.stop()

    def load_files(self):
        files = []
        for f in os.listdir(self.directory):
            if f.endswith(".mp3") or f.endswith(".ogg") or f.endswith(".wav"):
                files.append(self.directory + f)
        print(files)
        return files

class GalaxyNewsRadio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'Galaxy News Radio'
        self.directory = 'sounds/radio/gnr/'
        super(GalaxyNewsRadio, self).__init__(*args, **kwargs)

class DiamondCityRadio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'Diamond City Radio'
        self.directory = 'sounds/radio/DCR/'
        super(DiamondCityRadio, self).__init__(*args, **kwargs)

class EnclaveRadio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'Enclave Radio'
        self.directory = 'sounds/radio/Enclave/'
        super(EnclaveRadio, self).__init__(*args, **kwargs)

class InstituteRadio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'Institute Radio'
        self.directory = 'sounds/radio/Institute/'
        super(InstituteRadio, self).__init__(*args, **kwargs)

class MinutemenRadio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'Minutemen Radio'
        self.directory = 'sounds/radio/Minutemen/'
        super(MinutemenRadio, self).__init__(*args, **kwargs)

class Vault101Radio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'Vault 101 Radio'
        self.directory = 'sounds/radio/V101/'
        super(Vault101Radio, self).__init__(*args, **kwargs)

class ViolinRadio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'Violin Radio'
        self.directory = 'sounds/radio/Violin/'
        super(ViolinRadio, self).__init__(*args, **kwargs)

class F3Radio(RadioStation):
    def __init__(self, *args, **kwargs):
        self.label = 'F3 Radio'
        self.directory = 'sounds/radio/F3/'
        super(F3Radio, self).__init__(*args, **kwargs)