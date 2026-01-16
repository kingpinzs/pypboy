import pygame
import time
import config
import numpy as np

class Engine(object):

    EVENTS_UPDATE = pygame.USEREVENT + 1
    EVENTS_RENDER = pygame.USEREVENT + 2

    def __init__(self, title, width, height, *args, **kwargs):
        super(Engine, self).__init__(*args, **kwargs)
        #self.window = pygame.display.set_mode((width, height),pygame.FULLSCREEN)
        pygame.init()
        self.window = pygame.display.set_mode((width, height))
        self.screen = pygame.display.get_surface()
        pygame.display.set_caption(title)
        # Show cursor on desktop, hide on Pi (touch mode)
        pygame.mouse.set_visible(config.SHOW_CURSOR)

        self.groups = []
        self.root_children = EntityGroup()
        self.background = pygame.surface.Surface(self.screen.get_size()).convert()
        self.background.fill((0, 0, 0))

        self.rescale = False
        self.last_render_time = 0

        # Initialize CRT barrel distortion effect
        self.crt_enabled = getattr(config, 'CRT_EFFECT_ENABLED', True)
        self.crt_strength = getattr(config, 'CRT_EFFECT_STRENGTH', 0.15)
        if self.crt_enabled:
            self._init_crt_distortion(width, height)

    def _init_crt_distortion(self, width, height):
        """Pre-compute CRT barrel distortion mapping for performance using vectorized numpy."""
        # Create coordinate grids
        y_coords, x_coords = np.mgrid[0:height, 0:width].astype(np.float32)

        cx, cy = width / 2, height / 2

        # Normalize coordinates to -1 to 1
        nx = (x_coords - cx) / cx
        ny = (y_coords - cy) / cy

        # Calculate distance from center
        r = np.sqrt(nx * nx + ny * ny)

        # Apply barrel distortion formula: r' = r * (1 + k * r^2)
        factor = 1 + self.crt_strength * r * r

        # Apply distortion - keep as float for bilinear interpolation
        self.crt_src_x = nx_dist_px = nx * factor * cx + cx
        self.crt_src_y = ny_dist_px = ny * factor * cy + cy

        # Create mask for out-of-bounds pixels
        self.crt_mask = (nx_dist_px >= 0) & (nx_dist_px < width - 1) & \
                       (ny_dist_px >= 0) & (ny_dist_px < height - 1)

    def apply_crt_effect(self, surface):
        """Apply CRT barrel distortion with bilinear interpolation for smooth edges."""
        if not self.crt_enabled:
            return surface

        try:
            # Get pixel array from surface (shape: width x height x 3)
            src_array = pygame.surfarray.array3d(surface).astype(np.float32)
            height, width = self.crt_src_x.shape

            # Bilinear interpolation coordinates
            x0 = np.floor(self.crt_src_x).astype(np.int32)
            y0 = np.floor(self.crt_src_y).astype(np.int32)
            x1 = np.clip(x0 + 1, 0, src_array.shape[0] - 1)
            y1 = np.clip(y0 + 1, 0, src_array.shape[1] - 1)
            x0 = np.clip(x0, 0, src_array.shape[0] - 1)
            y0 = np.clip(y0, 0, src_array.shape[1] - 1)

            # Fractional parts for interpolation weights
            fx = (self.crt_src_x - np.floor(self.crt_src_x)).T
            fy = (self.crt_src_y - np.floor(self.crt_src_y)).T

            # Sample four corners and interpolate
            c00 = src_array[x0.T, y0.T]
            c10 = src_array[x1.T, y0.T]
            c01 = src_array[x0.T, y1.T]
            c11 = src_array[x1.T, y1.T]

            # Bilinear interpolation
            fx = fx[:, :, np.newaxis]
            fy = fy[:, :, np.newaxis]
            dst_array = (c00 * (1 - fx) * (1 - fy) +
                        c10 * fx * (1 - fy) +
                        c01 * (1 - fx) * fy +
                        c11 * fx * fy).astype(np.uint8)

            # Apply mask to black out pixels that map outside bounds
            dst_array[~self.crt_mask.T] = [0, 0, 0]

            # Create new surface from distorted array
            result = pygame.surfarray.make_surface(dst_array)
            return result
        except Exception:
            # If CRT effect fails, return original surface
            return surface

    def render(self):
        if self.last_render_time == 0:
            self.last_render_time = time.time()
            return
        else:
            interval = time.time() - self.last_render_time
            self.last_render_time = time.time()
        # Fill with black background
        self.screen.fill((0, 0, 0))
        # Draw content first (modules)
        for group in self.groups:
            group.render(interval)
            group.draw(self.screen)
            # Draw module's footer if it has one
            if hasattr(group, 'footer'):
                self.screen.blit(group.footer.image, group.footer.rect)
        # Draw scanlines overlay LAST (on top with additive blend)
        self.root_children.render(interval)
        for sprite in self.root_children:
            self.screen.blit(sprite.image, sprite.rect, special_flags=pygame.BLEND_RGBA_ADD)

        # Apply CRT barrel distortion effect
        if self.crt_enabled:
            distorted = self.apply_crt_effect(self.screen)
            self.screen.blit(distorted, (0, 0))

        pygame.display.flip()
        return interval

    def update(self):
        self.root_children.update()
        for group in self.groups:
            group.update()

    def add(self, group):
        if group not in self.groups:
            self.groups.append(group)

    def remove(self, group):
        if group in self.groups:
            self.groups.remove(group)


class EntityGroup(pygame.sprite.LayeredDirty):
    def render(self, interval):
        for entity in self:
            entity.render(interval)

    def move(self, x, y):
        for child in self:
            child.rect.move(x, y)


class Entity(pygame.sprite.DirtySprite):
    def __init__(self, dimensions=(0, 0), layer=0, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.image = pygame.surface.Surface(dimensions)
        self.rect = self.image.get_rect()
        self.image = self.image.convert()
        self.groups = pygame.sprite.LayeredDirty()
        self.layer = layer
        self.dirty = 1  # Redraw once, then stop (not 2 which means "always redraw")
        self.blendmode = 0  # Normal blending for content

    def render(self, interval=0, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass
