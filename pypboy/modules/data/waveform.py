import game
import pygame
import math
import config
from pypboy.modules.data.waveform_cache import waveform_cache


class RadioWaveform(game.Entity):
    """
    Real-time waveform visualization for the radio module.
    Displays actual audio waveform data from cached analysis.
    Matches Fallout Pip-Boy aesthetic with axis tick marks.
    """

    # Pip-Boy green colors (use config if available, else defaults)
    COLOR_PRIMARY = getattr(config, 'RADIO_WAVEFORM_COLOR', (95, 255, 177))
    COLOR_SECONDARY = getattr(config, 'RADIO_WAVEFORM_AXIS_COLOR', (60, 180, 120))
    COLOR_DIM = (40, 120, 80)         # Dim green for flat line

    # How many seconds of audio to show in the visualization window
    DISPLAY_WINDOW = 3.0  # Show 3 seconds of waveform

    def __init__(self, width=240, height=180):
        super(RadioWaveform, self).__init__((width, height))
        self.width = width
        self.height = height
        self.is_playing = False
        self.current_file = None
        self.time_offset = 0.0

        # Calculate plot area with margins for axes
        self.margin_left = 5
        self.margin_right = 20   # Space for right axis
        self.margin_bottom = 15  # Space for bottom axis
        self.margin_top = 5

        self.plot_x = self.margin_left
        self.plot_y = self.margin_top
        self.plot_width = self.width - self.margin_left - self.margin_right
        self.plot_height = self.height - self.margin_top - self.margin_bottom
        self.center_y = self.plot_y + self.plot_height // 2

        # Pre-draw static axes
        self._draw_axes()

    def _draw_axes(self):
        """Draw the static axis tick marks on background."""
        self.image.fill((0, 0, 0))

        # Draw right vertical axis (amplitude)
        axis_x = self.width - self.margin_right + 5
        pygame.draw.line(
            self.image, self.COLOR_SECONDARY,
            (axis_x, self.plot_y),
            (axis_x, self.plot_y + self.plot_height), 2
        )

        # Draw tick marks on right axis (every 20 pixels)
        for y in range(self.plot_y, self.plot_y + self.plot_height + 1, 20):
            tick_len = 6 if (y - self.plot_y) % 40 == 0 else 3
            pygame.draw.line(
                self.image, self.COLOR_SECONDARY,
                (axis_x - tick_len, y), (axis_x, y), 1
            )

        # Draw bottom horizontal axis (time)
        axis_y = self.plot_y + self.plot_height + 5
        pygame.draw.line(
            self.image, self.COLOR_SECONDARY,
            (self.plot_x, axis_y),
            (self.plot_x + self.plot_width, axis_y), 2
        )

        # Draw tick marks on bottom axis
        for x in range(self.plot_x, self.plot_x + self.plot_width + 1, 15):
            # Alternating long/short ticks
            tick_len = 6 if (x - self.plot_x) % 45 == 0 else 3
            pygame.draw.line(
                self.image, self.COLOR_SECONDARY,
                (x, axis_y), (x, axis_y + tick_len), 1
            )

        # Store background for fast redraw
        self.background = self.image.copy()

        # Draw initial flat line
        self._draw_flat_line()

    def _draw_flat_line(self):
        """Draw a flat line when not playing."""
        pygame.draw.line(
            self.image, self.COLOR_DIM,
            (self.plot_x, self.center_y),
            (self.plot_x + self.plot_width, self.center_y), 1
        )

    def set_audio_file(self, filepath):
        """Set the current audio file for visualization."""
        self.current_file = filepath
        # Pre-cache the waveform data (will analyze if not cached)
        if filepath:
            waveform_cache.get_waveform(filepath)

    def set_playing(self, playing, filepath=None):
        """Set the playing state and optionally update the audio file."""
        self.is_playing = playing
        if filepath:
            self.set_audio_file(filepath)

        if not playing:
            # Reset to flat line
            self.image.blit(self.background, (0, 0))
            self._draw_flat_line()
            self.dirty = 1

    def render(self, interval):
        """Render the waveform using real audio data."""
        if not self.is_playing:
            return

        # Get current playback position
        music_pos = 0
        if config.SOUND_ENABLED:
            try:
                if pygame.mixer.music.get_busy():
                    music_pos = pygame.mixer.music.get_pos() / 1000.0
            except:
                pass

        self.time_offset += interval

        # Clear to background (with axes)
        self.image.blit(self.background, (0, 0))

        # Get waveform data
        if self.current_file:
            # Get amplitude data for the display window centered on current position
            start_time = max(0, music_pos - self.DISPLAY_WINDOW / 2)
            end_time = music_pos + self.DISPLAY_WINDOW / 2

            amplitudes = waveform_cache.get_amplitude_range(
                self.current_file,
                start_time,
                end_time,
                self.plot_width
            )

            # Generate waveform points from real audio data
            points = []
            for i, amp in enumerate(amplitudes):
                x = self.plot_x + i

                # Create wave effect - oscillate based on amplitude
                # This creates the characteristic "audio waveform" look
                wave_offset = math.sin(music_pos * 20 + i * 0.3) * amp

                # Scale amplitude to plot area
                y = self.center_y - int(wave_offset * self.plot_height * 0.45)
                y = max(self.plot_y, min(self.plot_y + self.plot_height, y))

                points.append((x, y))

            # Draw waveform line
            if len(points) > 1:
                pygame.draw.lines(self.image, self.COLOR_PRIMARY, False, points, 2)
        else:
            # Fallback: simple animated line if no audio file
            self._draw_flat_line()

        self.dirty = 1
