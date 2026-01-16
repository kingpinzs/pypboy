import pypboy
import pygame
import game
import config
import pypboy.ui


class Module(pypboy.SubModule):

    label = "Status"

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

        # Create the body condition display (CND)
        self.health = Health()
        self.health.rect[0] = 100
        self.health.rect[1] = 40
        self.add(self.health)

        # Create status meters for RAD, H2O, FOD, SLP
        self.rad_meter = StatusMeter("RADIATION LEVEL", value=85, max_val=1000,
                                     danger_threshold=500)
        self.rad_meter.rect[0] = 100
        self.rad_meter.rect[1] = 60
        self.add(self.rad_meter)
        self.rad_meter.visible = 0

        self.h2o_meter = StatusMeter("HYDRATION", value=150, max_val=1000,
                                     danger_threshold=400, invert_danger=True)
        self.h2o_meter.rect[0] = 100
        self.h2o_meter.rect[1] = 60
        self.add(self.h2o_meter)
        self.h2o_meter.visible = 0

        self.fod_meter = StatusMeter("FOOD", value=200, max_val=1000,
                                     danger_threshold=400, invert_danger=True)
        self.fod_meter.rect[0] = 100
        self.fod_meter.rect[1] = 60
        self.add(self.fod_meter)
        self.fod_meter.visible = 0

        self.slp_meter = StatusMeter("SLEEP", value=320, max_val=1000,
                                     danger_threshold=400, invert_danger=True)
        self.slp_meter.rect[0] = 100
        self.slp_meter.rect[1] = 60
        self.add(self.slp_meter)
        self.slp_meter.visible = 0

        # Create effects list
        self.effects_list = EffectsList()
        self.effects_list.rect[0] = 100
        self.effects_list.rect[1] = 60
        self.add(self.effects_list)
        self.effects_list.visible = 0

        # Track current display
        self.current_display = 'cnd'
        self.displays = {
            'cnd': self.health,
            'rad': self.rad_meter,
            'eff': self.effects_list,
            'h2o': self.h2o_meter,
            'fod': self.fod_meter,
            'slp': self.slp_meter
        }

        # Create the side menu
        self.menu = pypboy.ui.Menu(100, ["CND", "RAD", "EFF", "H2O", "FOD", "SLP"],
                                   [self.show_cnd, self.show_rad, self.show_eff,
                                    self.show_h2o, self.show_fod, self.show_slp], 0)
        self.menu.rect[0] = 4
        self.menu.rect[1] = 60
        self.add(self.menu)

    def _switch_display(self, display_name):
        """Switch to showing a specific display, hiding others."""
        for name, display in self.displays.items():
            if name == display_name:
                display.visible = 1
                display.dirty = 2
            else:
                display.visible = 0
        self.current_display = display_name

    def show_cnd(self):
        self._switch_display('cnd')

    def show_rad(self):
        self._switch_display('rad')

    def show_eff(self):
        self._switch_display('eff')

    def show_h2o(self):
        self._switch_display('h2o')

    def show_fod(self):
        self._switch_display('fod')

    def show_slp(self):
        self._switch_display('slp')


class Health(game.Entity):
    """Body condition diagram display - Fallout 3 style.

    The pipboyfallout3.png image has bar outlines, we fill them in.
    """

    def __init__(self, player_name="Jeromy", player_level=3):
        # Create surface to fit the display area
        width = 360
        height = 220
        super(Health, self).__init__((width, height))

        self.color = (95, 255, 177)
        self.bar_color = (200, 170, 55)  # Amber/gold color like Fallout
        self.player_name = player_name
        self.player_level = player_level

        # Body part conditions (0-100, 100 = perfect)
        self.limb_conditions = {
            'head': 100,
            'left_arm': 100,
            'right_arm': 100,
            'torso': 100,
            'left_leg': 100,
            'right_leg': 100
        }

        # Healing items in inventory (matching reference)
        self.healing_items = [
            ("Stimpak $", 23),
            ("Doctor's Bag E", 3),
        ]

        # Store image offset for bar positioning
        self.img_x = 0
        self.img_y = 0
        self.scale_factor = 1.0

        self._redraw()

    def _redraw(self):
        """Redraw the condition display."""
        self.image.fill((0, 0, 0))

        # Load and draw Vault Boy image
        try:
            vault_boy = pygame.image.load('images/pipboyfallout3.png')
            orig_width, orig_height = vault_boy.get_size()

            # Scale to fit
            vb_height = 180
            self.scale_factor = vb_height / orig_height
            vb_width = int(orig_width * self.scale_factor)
            vault_boy = pygame.transform.smoothscale(vault_boy, (vb_width, vb_height))

            # Center horizontally
            self.img_x = (self.image.get_width() - vb_width) // 2 - 30
            self.img_y = 0
            self.image.blit(vault_boy, (self.img_x, self.img_y))

            # Fill in the health bars
            self._fill_health_bars()

        except Exception as e:
            pass

        # Draw healing items list on right side
        self._draw_items_list()

        # Draw player name and level at bottom center
        name_text = f"{self.player_name} - Level {self.player_level}"
        name_surface = config.FONTS[14].render(name_text, True, self.color, (0, 0, 0))
        name_x = (self.image.get_width() - name_surface.get_width()) // 2 - 30
        name_y = 185
        self.image.blit(name_surface, (name_x, name_y))

    def _fill_health_bars(self):
        """Fill in the health bars on the Vault Boy image."""
        # Bar positions in original image coordinates (2016x2112)
        # These positions are calibrated to the pipboyfallout3.png image lines
        # Format: (limb, x, y, width, height) in original image pixels
        bar_positions = [
            # Left side bars - thicker bars for visibility
            ('head', 880, 40, 270, 40),        # Head bar - connects to head
            ('left_arm', 100, 450, 270, 40),    # Left arm bar - upper left
            ('left_leg', 100, 1460, 300, 40),   # Left leg bar - lower left
            # Right side bars
            ('right_arm', 1650, 420, 300, 40),  # Right arm bar - upper right
            ('right_leg', 1678, 1440, 300, 40), # Right leg bar - lower right
        ]

        for limb, orig_x, orig_y, orig_w, orig_h in bar_positions:
            condition = self.limb_conditions.get(limb, 100)

            # Scale coordinates to current image size
            x = int(orig_x * self.scale_factor) + self.img_x
            y = int(orig_y * self.scale_factor) + self.img_y
            w = int(orig_w * self.scale_factor)
            h = int(orig_h * self.scale_factor)

            # Calculate fill width based on condition
            fill_w = int(w * condition / 100)

            if fill_w > 0:
                pygame.draw.rect(self.image, self.bar_color, (x, y, fill_w, h))

    def _draw_items_list(self):
        """Draw healing items list on right side."""
        x_offset = 270
        y_offset = 20

        for item_name, count in self.healing_items[:4]:
            item_text = f"({count}) {item_name}"
            item_surface = config.FONTS[11].render(item_text, True, self.color, (0, 0, 0))
            self.image.blit(item_surface, (x_offset, y_offset))
            y_offset += 20

    def set_limb_condition(self, limb, value):
        """Set condition for a specific limb."""
        if limb in self.limb_conditions:
            self.limb_conditions[limb] = max(0, min(100, value))
            self._redraw()
            self.dirty = 2

    def set_player_info(self, name, level):
        """Update player name and level."""
        self.player_name = name
        self.player_level = level
        self._redraw()
        self.dirty = 2


class StatusMeter(game.Entity):
    """Horizontal status meter with scale markings (Fallout 3 style)."""

    def __init__(self, label, value=0, max_val=1000, danger_threshold=500,
                 invert_danger=False):
        # Meter dimensions
        width = 340
        height = 200
        super(StatusMeter, self).__init__((width, height))

        self.label = label
        self.value = value
        self.max_val = max_val
        self.danger_threshold = danger_threshold
        self.invert_danger = invert_danger  # True = low values are dangerous

        self.color = (95, 255, 177)
        self.danger_color = (255, 80, 80)

        self._redraw()

    def _redraw(self):
        """Redraw the meter display."""
        self.image.fill((0, 0, 0))

        # Draw label
        label_text = config.FONTS[16].render(self.label, True, self.color, (0, 0, 0))
        self.image.blit(label_text, (10, 10))

        # Meter position and size
        meter_x = 10
        meter_y = 50
        meter_width = 300
        meter_height = 20

        # Draw meter outline
        pygame.draw.rect(self.image, self.color,
                        (meter_x, meter_y, meter_width, meter_height), 2)

        # Calculate fill width
        fill_ratio = self.value / self.max_val
        fill_width = int((meter_width - 4) * fill_ratio)

        # Determine color based on danger
        if self.invert_danger:
            is_danger = self.value < self.danger_threshold
        else:
            is_danger = self.value > self.danger_threshold

        fill_color = self.danger_color if is_danger else self.color

        # Draw filled portion
        if fill_width > 0:
            pygame.draw.rect(self.image, fill_color,
                           (meter_x + 2, meter_y + 2, fill_width, meter_height - 4))

        # Draw scale markings
        scale_y = meter_y + meter_height + 5

        # Draw tick marks at 0, 250, 500, 750, 1000
        tick_positions = [0, 0.25, 0.5, 0.75, 1.0]
        tick_labels = ["0", "250", "500", "750", "1000"]

        for i, pos in enumerate(tick_positions):
            tick_x = meter_x + int(meter_width * pos)
            # Draw tick
            pygame.draw.line(self.image, self.color,
                           (tick_x, scale_y), (tick_x, scale_y + 8), 1)
            # Draw label
            tick_text = config.FONTS[10].render(tick_labels[i], True, self.color, (0, 0, 0))
            text_x = tick_x - tick_text.get_width() // 2
            self.image.blit(tick_text, (text_x, scale_y + 10))

        # Draw horizontal scale line
        pygame.draw.line(self.image, self.color,
                        (meter_x, scale_y), (meter_x + meter_width, scale_y), 1)

        # Draw current value
        value_text = config.FONTS[14].render(f"{self.value}/{self.max_val}",
                                             True, self.color, (0, 0, 0))
        self.image.blit(value_text, (meter_x + meter_width + 10, meter_y))

        # Draw status text
        if self.invert_danger:
            if self.value < 200:
                status = "CRITICAL"
                status_color = self.danger_color
            elif self.value < 400:
                status = "LOW"
                status_color = (255, 200, 100)
            else:
                status = "NORMAL"
                status_color = self.color
        else:
            if self.value > 800:
                status = "CRITICAL"
                status_color = self.danger_color
            elif self.value > 500:
                status = "HIGH"
                status_color = (255, 200, 100)
            else:
                status = "NORMAL"
                status_color = self.color

        status_text = config.FONTS[14].render(status, True, status_color, (0, 0, 0))
        self.image.blit(status_text, (10, 100))

        # Draw description based on meter type
        descriptions = {
            "RADIATION LEVEL": [
                "Radiation exposure from the",
                "wasteland environment.",
                "",
                "Seek RadAway to reduce levels."
            ],
            "HYDRATION": [
                "Water intake levels.",
                "Drink purified water regularly",
                "to maintain hydration.",
                ""
            ],
            "FOOD": [
                "Nutritional status.",
                "Consume food items to",
                "maintain energy levels.",
                ""
            ],
            "SLEEP": [
                "Rest and fatigue levels.",
                "Find a bed to sleep and",
                "restore energy.",
                ""
            ]
        }

        desc_lines = descriptions.get(self.label, [])
        desc_y = 130
        for line in desc_lines:
            if line:
                desc_text = config.FONTS[12].render(line, True, self.color, (0, 0, 0))
                self.image.blit(desc_text, (10, desc_y))
            desc_y += 16

    def set_value(self, value):
        """Update the meter value."""
        self.value = max(0, min(value, self.max_val))
        self._redraw()
        self.dirty = 2


class EffectsList(game.Entity):
    """Display list of active effects."""

    def __init__(self):
        width = 340
        height = 200
        super(EffectsList, self).__init__((width, height))

        self.color = (95, 255, 177)
        self.positive_color = (95, 255, 177)
        self.negative_color = (255, 100, 100)

        # Sample effects (positive effects, negative effects)
        self.effects = [
            ("Well Rested", "+10% XP", True),
            ("Rad Resistance", "+25 Rad Resist", True),
            ("Night Person", "+2 INT, +2 PER (Night)", True),
            ("Dehydration", "-1 END", False),
            ("Minor Radiation Poisoning", "-1 END", False),
        ]

        self._redraw()

    def _redraw(self):
        """Redraw the effects list."""
        self.image.fill((0, 0, 0))

        # Draw header
        header_text = config.FONTS[16].render("ACTIVE EFFECTS", True, self.color, (0, 0, 0))
        self.image.blit(header_text, (10, 10))

        # Draw separator line
        pygame.draw.line(self.image, self.color, (10, 35), (320, 35), 1)

        if not self.effects:
            no_effects = config.FONTS[14].render("No active effects", True, self.color, (0, 0, 0))
            self.image.blit(no_effects, (10, 50))
            return

        # Draw effects
        y_offset = 45
        for effect_name, effect_value, is_positive in self.effects:
            color = self.positive_color if is_positive else self.negative_color

            # Draw effect name
            name_text = config.FONTS[12].render(effect_name, True, color, (0, 0, 0))
            self.image.blit(name_text, (15, y_offset))

            # Draw effect value
            value_text = config.FONTS[12].render(effect_value, True, color, (0, 0, 0))
            self.image.blit(value_text, (220, y_offset))

            y_offset += 22

    def add_effect(self, name, value, is_positive=True):
        """Add an effect to the list."""
        self.effects.append((name, value, is_positive))
        self._redraw()
        self.dirty = 2

    def remove_effect(self, name):
        """Remove an effect by name."""
        self.effects = [(n, v, p) for n, v, p in self.effects if n != name]
        self._redraw()
        self.dirty = 2
