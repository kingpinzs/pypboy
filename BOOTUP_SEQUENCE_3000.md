# BOOTUP SEQUENCE 3000
## PIP-OS(R) V7.1.0.8 Boot Animation Specification

---

## Overview

Authentic Fallout 4 PIP-OS boot sequence with character-by-character typewriter effect, blinking block cursor, line-by-line pauses, and scroll-up transition.

---

## Boot Sequence Text

```
************** PIP-OS(R) V7.1.0.8 **************

COPYRIGHT 2075 ROBCO(R)
LOADER V1.1
EXEC VERSION 41.10
64k RAM SYSTEM
38911 BYTES FREE
NO HOLOTAPE FOUND
LOAD ROM(1): DEITRIX 303
```

---

## Animation Phases

### Phase 1: Initial Cursor
- Screen is black
- Blinking block cursor (█) appears at top-left
- Cursor blinks 2-3 times before typing begins
- Duration: ~1.5 seconds

### Phase 2: Header Line
- Types: `************** PIP-OS(R) V7.1.0.8 **************`
- Character-by-character with cursor following
- Speed: ~40ms per character
- After complete: cursor moves to next line

### Phase 3: Blank Line Pause
- Cursor on line 2 (empty line)
- Cursor blinks 2-3 times
- Duration: ~1.5 seconds

### Phase 4: Boot Lines (Repeat for each)
For each line (COPYRIGHT through LOAD ROM):
1. Type line character-by-character (~40ms/char)
2. Cursor moves to next line
3. Cursor blinks 2-3 times (~1.5 seconds)
4. Repeat for next line

### Phase 5: Final Pause
- All text displayed
- Cursor blinks at end of last line
- Duration: ~1 second

### Phase 6: Scroll Up
- All text scrolls upward smoothly
- Speed: ~300 pixels/second
- Duration: ~1 second until all text off-screen

### Phase 7: Transition
- Screen clears to black
- Main Pypboy interface loads

---

## Cursor Specification

### Appearance
- Block cursor: `█` (Unicode U+2588) or filled rectangle
- Color: `(105, 255, 187)` - Pip-Boy green
- Size: Same as font character cell

### Behavior
- Blink rate: 500ms visible, 500ms hidden
- Position: Immediately after last typed character
- During typing: Always visible (no blink)
- During pause: Blinks on/off

---

## Timing Constants

| Parameter | Value | Description |
|-----------|-------|-------------|
| `CHAR_DELAY` | 40ms | Time between each character |
| `CURSOR_BLINK` | 500ms | Cursor on/off interval |
| `LINE_PAUSE_BLINKS` | 3 | Number of cursor blinks between lines |
| `SCROLL_SPEED` | 300px/s | Scroll-up animation speed |
| `INITIAL_BLINKS` | 3 | Cursor blinks before typing starts |

---

## Implementation Architecture

### File: `pypboy/boot.py`

```python
import pygame
import time
import config

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

        # Calculate line height from font
        self.line_height = self.font.get_linesize()
        self.start_x = 20  # Left margin
        self.start_y = 40  # Top margin

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
        self.char_delay = config.BOOT_CHAR_DELAY
        self.blink_interval = config.BOOT_CURSOR_BLINK
        self.line_pause_blinks = config.BOOT_LINE_PAUSE_BLINKS
        self.scroll_speed = config.BOOT_SCROLL_SPEED

    def run(self):
        """Main boot sequence loop - blocks until complete"""
        clock = pygame.time.Clock()
        self.last_blink_time = time.time()
        self.last_char_time = time.time()

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

            # Update state
            self.update()

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
            if self.blink_count >= config.BOOT_INITIAL_BLINKS:
                self.phase = "typing"
                self.blink_count = 0
                self.cursor_visible = True

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
                        # All lines done
                        self.phase = "scroll"
                    else:
                        # Pause before next line
                        self.phase = "line_pause"
                        self.blink_count = 0

        elif self.phase == "line_pause":
            if self.blink_count >= self.line_pause_blinks:
                self.phase = "typing"
                self.blink_count = 0
                self.cursor_visible = True

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
                text_surface = self.font.render(line, True, self.color)
                self.screen.blit(text_surface, (self.start_x, y))
            y += self.line_height

        # Render current line being typed (if not scrolling)
        if self.phase in ("typing", "line_pause", "initial_blink"):
            if self.current_line_idx < len(self.BOOT_LINES):
                current_text = self.BOOT_LINES[self.current_line_idx][:self.current_char_idx]

                if y > -self.line_height and y < self.height:
                    if current_text:
                        text_surface = self.font.render(current_text, True, self.color)
                        self.screen.blit(text_surface, (self.start_x, y))

                    # Render cursor
                    if self.cursor_visible:
                        cursor_x = self.start_x + self.font.size(current_text)[0]
                        cursor_surface = self.font.render("█", True, self.color)
                        self.screen.blit(cursor_surface, (cursor_x, y))
```

---

## Configuration

### Add to `config.py`:

```python
# Boot Sequence Configuration
BOOT_SEQUENCE_ENABLED = True
BOOT_CHAR_DELAY = 0.04          # 40ms per character
BOOT_CURSOR_BLINK = 0.5         # 500ms cursor blink interval
BOOT_LINE_PAUSE_BLINKS = 3      # Cursor blinks between lines
BOOT_INITIAL_BLINKS = 3         # Cursor blinks before typing starts
BOOT_SCROLL_SPEED = 300         # Pixels per second for scroll-up
BOOT_SKIP_KEYS = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]
```

---

## Integration

### Modify `main.py`:

```python
# After pygame initialization and screen creation...

if config.BOOT_SEQUENCE_ENABLED:
    from pypboy.boot import BootSequence
    boot = BootSequence(screen)
    boot.run()

# Continue with Pypboy initialization...
boy = pypboy.Pypboy()
boy.run()
```

---

## Files Summary

| Action | File | Description |
|--------|------|-------------|
| CREATE | `pypboy/boot.py` | BootSequence class implementation |
| MODIFY | `config.py` | Add boot configuration constants |
| MODIFY | `main.py` | Integrate boot sequence before Pypboy |

---

## Verification Checklist

- [ ] Blinking cursor appears on black screen first
- [ ] Header line types character-by-character
- [ ] Cursor blinks between each line
- [ ] All 8 boot lines display correctly
- [ ] Smooth scroll-up animation at end
- [ ] Skip works with Space/Enter/Escape
- [ ] Skip works with mouse click
- [ ] Clean transition to main Pypboy interface
- [ ] Works on desktop (pygame window)
- [ ] Works on Raspberry Pi with touchscreen

---

## Visual Reference

```
Frame 1 (t=0.0s):     █                              <- cursor blinks alone
Frame 2 (t=1.5s):     *█                             <- typing starts
Frame 3 (t=1.6s):     **█
...
Frame N:              ************** PIP-OS(R) V7.1.0.8 **************
                      █                              <- cursor on line 2, blinking
...
Frame N+M:            ************** PIP-OS(R) V7.1.0.8 **************

                      COPYRIGHT 2075 ROBCO(R)
                      █                              <- cursor blinking
...
Final:                [all text scrolls up and off screen]
```
