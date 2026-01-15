import pypboy
import config
import pygame

from pypboy.modules.data import entities
from pypboy.modules.data.waveform import RadioWaveform


class Module(pypboy.SubModule):

    label = "Radio"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        # Create stations list with OFF at top (Fallout style)
        self.stations = [
            entities.RadioOff(),  # OFF option at index 0
            entities.GalaxyNewsRadio(),
            entities.DiamondCityRadio(),
            entities.EnclaveRadio(),
            entities.InstituteRadio(),
            entities.MinutemenRadio(),
            entities.Vault101Radio(),
            entities.ViolinRadio(),
            entities.F3Radio()
        ]

        # Only add actual RadioStation entities to the group (skip RadioOff)
        for station in self.stations:
            if hasattr(station, 'add'):
                self.add(station)

        self.active_station = None
        config.radio = self

        # Build menu labels and callbacks
        stationLabels = []
        stationCallbacks = []
        for i, station in enumerate(self.stations):
            stationLabels.append(station.label)
            stationCallbacks.append(lambda i=i: self.select_station(i))

        # Create waveform visualization FIRST (before menu selection triggers callback)
        self.waveform = RadioWaveform(width=240, height=180)
        self.waveform.rect[0] = 220  # Right side position
        self.waveform.rect[1] = 60   # Align with menu
        self.add(self.waveform)

        # Create menu on left side (selected=0 auto-selects OFF)
        self.menu = pypboy.ui.Menu(200, stationLabels, stationCallbacks, 0)
        self.menu.rect[0] = 4
        self.menu.rect[1] = 60
        self.add(self.menu)

    def select_station(self, station_index):
        """Select a radio station or turn OFF."""
        # Stop current station if one is active
        if hasattr(self, 'active_station') and self.active_station:
            self.active_station.stop()

        selected = self.stations[station_index]

        if station_index == 0:  # OFF selected
            self.active_station = None
            if hasattr(self, 'waveform'):
                self.waveform.set_playing(False)
            # Stop any playing music immediately
            if config.SOUND_ENABLED:
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
        else:
            self.active_station = selected
            self.active_station.play_random()
            if hasattr(self, 'waveform'):
                self.waveform.set_playing(True)

    def handle_event(self, event):
        """Handle song end event to play next track."""
        if event.type == config.EVENTS['SONG_END']:
            if hasattr(self, 'active_station') and self.active_station:
                self.active_station.play_random()

    def render(self, interval):
        """Render the waveform animation."""
        if hasattr(self, 'waveform'):
            self.waveform.render(interval)
        super(Module, self).render(interval)

    def handle_resume(self):
        self.parent.pypboy.header.headline = "DATA"
        self.parent.pypboy.header.title = ["Radio"]
        super(Module, self).handle_resume()
