import game
import pygame
import math
import config


class RadioWaveform(game.Entity):
    """
    Animated waveform visualization for the radio module.
    Matches Fallout Pip-Boy aesthetic with axis tick marks.
    Displays a modulated sine wave when playing, flat line when stopped.
    """

    # Pip-Boy green colors (use config if available, else defaults)
    COLOR_PRIMARY = getattr(config, 'RADIO_WAVEFORM_COLOR', (95, 255, 177))
    COLOR_SECONDARY = getattr(config, 'RADIO_WAVEFORM_AXIS_COLOR', (60, 180, 120))
    COLOR_DIM = (40, 120, 80)         # Dim green for flat line

    def __init__(self, width=240, height=180):
        super(RadioWaveform, self).__init__((width, height))
        self.width = width
        self.height = height
        self.is_playing = False
        self.time_offset = 0.0

        # Waveform parameters
        self.wave_frequency = 0.15
        self.amplitude_base = 0.3
        self.amplitude_mod = 0.5

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

    def set_playing(self, playing):
        """Set the playing state."""
        self.is_playing = playing
        if not playing:
            # Reset to flat line
            self.image.blit(self.background, (0, 0))
            self._draw_flat_line()
            self.dirty = 1

    def render(self, interval):
        """Render the waveform animation."""
        if not self.is_playing:
            return

        # Get music position for animation timing
        music_pos = self.time_offset
        if config.SOUND_ENABLED:
            try:
                if pygame.mixer.music.get_busy():
                    music_pos = pygame.mixer.music.get_pos() / 1000.0
            except:
                pass

        self.time_offset += interval

        # Clear to background (with axes)
        self.image.blit(self.background, (0, 0))

        # Generate waveform points
        points = []
        for i in range(self.plot_width):
            x = self.plot_x + i

            # Create modulated sine wave similar to reference screenshot
            t = music_pos * 50 + i * self.wave_frequency

            # Multiple overlapping sine waves for complex waveform
            wave1 = math.sin(t * 1.0) * 0.5
            wave2 = math.sin(t * 2.3 + 1.5) * 0.3
            wave3 = math.sin(t * 0.7 + 0.8) * 0.2

            # Amplitude modulation to vary wave height over time
            amp_mod = 0.5 + 0.5 * math.sin(music_pos * 3 + i * 0.02)

            combined = (wave1 + wave2 + wave3) * amp_mod

            # Scale to plot area
            y = self.center_y - int(combined * self.plot_height * 0.4)
            y = max(self.plot_y, min(self.plot_y + self.plot_height, y))

            points.append((x, y))

        # Draw waveform line
        if len(points) > 1:
            pygame.draw.lines(self.image, self.COLOR_PRIMARY, False, points, 2)

        self.dirty = 1
