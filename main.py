import pygame
import optparse
import os
import sys
import config
from platform_detect import PLATFORM

parser = optparse.OptionParser(
    usage='python %prog -c True\nor:\npython %prog -c True',
    version="0.0.1",
    prog=sys.argv[0]
)
parser.add_option(
    '-c', '--cached-map',
    action="store_true",
    help="Loads the cached map file stored in map.cache",
    dest="load_cached",
    default=False
)
options, args = parser.parse_args()

# Detect platform and GPIO availability
PLATFORM.detect_gpio()
config.GPIO_AVAILABLE = PLATFORM.gpio_available
config.IS_RASPBERRY_PI = PLATFORM.is_raspberry_pi
config.SHOW_CURSOR = PLATFORM.is_desktop  # Show cursor on desktop, hide on Pi

print(f"Platform: {PLATFORM}")

# Set up framebuffer/touchscreen environment for Raspberry Pi
if config.GPIO_AVAILABLE:
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')
    os.putenv('SDL_MOUSEDEV', config.TOUCH_DEVICE)

from pypboy.core import Pypboy

# Initialize sound
try:
    pygame.mixer.init(44100, -16, 2, 2048)
    config.SOUND_ENABLED = True
except Exception:
    config.SOUND_ENABLED = False

if __name__ == "__main__":
    boy = Pypboy('Pip-Boy 3000', config.WIDTH, config.HEIGHT)
    print("RUN")
    boy.run()
