"""
PIP-OS(R) V7.1.0.8 Boot Sequence
Authentic Fallout 4 style boot animation with typewriter effect and blinking cursor.
"""

import pygame
import time
import config
from pypboy.ui import Scanlines


class BootSequence:
    """PIP-OS V7.1.0.8 boot sequence with typewriter effect"""

    BOOT_LINES = [
        "************** PIP-OS(R) V7.1.0.8 **************",
        "",
        "COPYRIGHT 2075 ROBCO(R)",
        "LOADER V1.1",
        "EXEC VERSION 41.10",
        "64k RAM SYSTEM",
        "38911 BYTES FREE",
        "NO HOLOTAPE FOUND",
        "LOAD ROM(1): DEITRIX 303",
    ]

    def __init__(self, screen):
        self.screen = screen
        self.width = config.WIDTH
        self.height = config.HEIGHT
        self.font = config.FONTS[14]
        self.color = (105, 255, 187)
        self.bg_color = (0, 0, 0)

        # Calculate line height and cursor size from font
        self.line_height = self.font.get_linesize()
        self.cursor_width = self.font.size("M")[0]  # Width of a character
        self.cursor_height = self.line_height - 2
        self.start_x = 20  # Left margin
        self.start_y = 40  # Top margin

        # Scanlines overlay for CRT effect (same settings as main app)
        self.scanlines1 = Scanlines(
            800, 480, 3, 1,
            [(0, 4, 1, 12), (2, 12, 6, 25), (0, 4, 1, 12)]
        )
        self.scanlines2 = Scanlines(
            800, 480, 8, 40,
            [(0, 3, 0, 0), (6, 18, 12, 20), (18, 36, 24, 28), (6, 18, 12, 20)] + [(0, 3, 0, 0) for x in range(50)],
            True
        )

        # State
        self.completed_lines = []      # Fully typed lines
        self.current_line_idx = 0      # Which BOOT_LINE we're on
        self.current_char_idx = 0      # Character position in current line
        self.cursor_visible = True
        self.scroll_offset = 0         # For scroll-up animation

        # Phase: "initial_blink", "typing", "line_pause", "scroll", "done"
        self.phase = "initial_blink"
        self.blink_count = 0

        # Timing
        self.last_char_time = 0
        self.last_blink_time = 0
        self.last_render_time = 0
        self.char_delay = config.BOOT_CHAR_DELAY
        self.blink_interval = config.BOOT_CURSOR_BLINK
        self.line_pause_blinks = config.BOOT_LINE_PAUSE_BLINKS
        self.initial_blinks = config.BOOT_INITIAL_BLINKS
        self.scroll_speed = config.BOOT_SCROLL_SPEED

    def run(self):
        """Main boot sequence loop - blocks until complete"""
        clock = pygame.time.Clock()
        current_time = time.time()
        self.last_blink_time = current_time
        self.last_char_time = current_time
        self.last_render_time = current_time

        running = True
        while running and self.phase != "done":
            # Handle events (skip on input)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in config.BOOT_SKIP_KEYS:
                        return  # Skip boot sequence
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    return  # Skip on click

            # Calculate interval for scanlines
            current_time = time.time()
            interval = current_time - self.last_render_time
            self.last_render_time = current_time

            # Update state
            self.update()

            # Update scanlines
            self.scanlines1.render(interval)
            self.scanlines2.render(interval)

            # Render
            self.render()
            pygame.display.flip()

            clock.tick(60)  # 60 FPS

    def update(self):
        """Update boot sequence state"""
        current_time = time.time()

        # Handle cursor blinking
        if current_time - self.last_blink_time >= self.blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_blink_time = current_time

            # Count blinks during pause phases
            if self.phase in ("initial_blink", "line_pause"):
                if not self.cursor_visible:  # Count on cursor hide
                    self.blink_count += 1

        # Phase-specific updates
        if self.phase == "initial_blink":
            if self.blink_count >= self.initial_blinks:
                self.phase = "typing"
                self.blink_count = 0
                self.cursor_visible = True
                self.last_char_time = current_time

        elif self.phase == "typing":
            # Type next character
            if current_time - self.last_char_time >= self.char_delay:
                current_line = self.BOOT_LINES[self.current_line_idx]

                if self.current_char_idx < len(current_line):
                    self.current_char_idx += 1
                    self.last_char_time = current_time
                    self.cursor_visible = True  # Keep cursor visible while typing
                else:
                    # Line complete
                    self.completed_lines.append(current_line)
                    self.current_line_idx += 1
                    self.current_char_idx = 0

                    if self.current_line_idx >= len(self.BOOT_LINES):
                        # All lines done - brief pause then scroll
                        self.phase = "line_pause"
                        self.blink_count = 0
                        self.line_pause_blinks = 2  # Shorter final pause
                    else:
                        # Pause before next line
                        self.phase = "line_pause"
                        self.blink_count = 0

        elif self.phase == "line_pause":
            if self.blink_count >= self.line_pause_blinks:
                if self.current_line_idx >= len(self.BOOT_LINES):
                    # All lines done, start scroll
                    self.phase = "scroll"
                else:
                    self.phase = "typing"
                    self.blink_count = 0
                    self.cursor_visible = True
                    self.last_char_time = current_time

        elif self.phase == "scroll":
            # Scroll all text upward
            self.scroll_offset += self.scroll_speed / 60  # Assuming 60 FPS

            # Check if all text scrolled off screen
            total_height = len(self.completed_lines) * self.line_height + self.start_y
            if self.scroll_offset >= total_height:
                self.phase = "done"

    def render(self):
        """Render current boot state"""
        self.screen.fill(self.bg_color)

        y = self.start_y - self.scroll_offset

        # Render completed lines
        for line in self.completed_lines:
            if y > -self.line_height and y < self.height:
                if line:  # Don't render empty lines
                    text_surface = self.font.render(line, True, self.color)
                    self.screen.blit(text_surface, (self.start_x, y))
            y += self.line_height

        # Render current line being typed (if not scrolling and not done)
        if self.phase in ("typing", "line_pause", "initial_blink"):
            if self.current_line_idx < len(self.BOOT_LINES):
                current_text = self.BOOT_LINES[self.current_line_idx][:self.current_char_idx]

                if y > -self.line_height and y < self.height:
                    # Render typed portion of current line
                    if current_text:
                        text_surface = self.font.render(current_text, True, self.color)
                        self.screen.blit(text_surface, (self.start_x, y))

                    # Render cursor as filled rectangle
                    if self.cursor_visible:
                        cursor_x = self.start_x
                        if current_text:
                            cursor_x += self.font.size(current_text)[0]
                        cursor_rect = pygame.Rect(
                            cursor_x, y + 1,
                            self.cursor_width, self.cursor_height
                        )
                        pygame.draw.rect(self.screen, self.color, cursor_rect)

        # Render scanlines overlay on top (with additive blend)
        self.screen.blit(self.scanlines1.image, self.scanlines1.rect, special_flags=pygame.BLEND_RGBA_ADD)
        self.screen.blit(self.scanlines2.image, self.scanlines2.rect, special_flags=pygame.BLEND_RGBA_ADD)
