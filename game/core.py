import pygame
import time
import config

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
        self.dirty = 2
        self.blendmode = 0  # Normal blending for content

    def render(self, interval=0, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass
