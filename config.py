import os
import pygame
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

WIDTH = 480
HEIGHT = 320

# OUTPUT_WIDTH = 320
# OUTPUT_HEIGHT = 240

# GPS coordinates from .env (longitude, latitude)
# Default: Santa Clarita, CA
_default_lon = -118.5723894
_default_lat = 34.3917171
MAP_FOCUS = (
    float(os.getenv('MAP_LONGITUDE', _default_lon)),
    float(os.getenv('MAP_LATITUDE', _default_lat))
)

# Load map from cache instead of internet
LOAD_CACHED_MAP = os.getenv('LOAD_CACHED_MAP', 'false').lower() in ('true', '1', 'yes')

# Map zoom configuration
MAP_ZOOM_MIN = 0.5               # Max zoomed out (see more area)
MAP_ZOOM_MAX = 3.0               # Max zoomed in (see less area)
MAP_ZOOM_DEFAULT = 1.0           # Starting zoom level
MAP_ZOOM_STEP = 0.15             # Zoom increment per keypress
MAP_SMOOTHSCALE = False          # False = faster (scale), True = prettier (smoothscale)

# World map settings (larger surface for extended panning)
WORLD_MAP_SURFACE_SIZE = 960     # 2x screen width for pan area
WORLD_MAP_RADIUS = 0.12          # Larger fetch radius (~27km)
WORLD_MAP_BUFFER = 100           # Pixels from edge to trigger expansion

# Platform-specific settings (set by main.py via platform_detect)
GPIO_AVAILABLE = False
IS_RASPBERRY_PI = False
SHOW_CURSOR = True  # True on desktop, False on Pi

# Touch input device (for Raspberry Pi with Adafruit TFT)
TOUCH_DEVICE = os.getenv('TOUCH_DEVICE', '/dev/input/event2')

# Sound settings
SOUND_ENABLED = True

# Radio waveform visualization settings
RADIO_WAVEFORM_WIDTH = 240
RADIO_WAVEFORM_HEIGHT = 180
RADIO_WAVEFORM_X = 220
RADIO_WAVEFORM_Y = 60
RADIO_WAVEFORM_COLOR = (95, 255, 177)
RADIO_WAVEFORM_AXIS_COLOR = (60, 180, 120)

EVENTS = {
    'SONG_END': pygame.USEREVENT + 1
}

ACTIONS = {
    pygame.K_F1: "module_stats",
    pygame.K_F2: "module_items",
    pygame.K_F3: "module_data",
    pygame.K_1:	"knob_1",
    pygame.K_2: "knob_2",
    pygame.K_3: "knob_3",
    pygame.K_4: "knob_4",
    pygame.K_5: "knob_5",
    pygame.K_UP: "dial_up",
    pygame.K_DOWN: "dial_down",
    pygame.K_PLUS: "zoom_in",
    pygame.K_MINUS: "zoom_out",
    pygame.K_KP_PLUS: "zoom_in",
    pygame.K_KP_MINUS: "zoom_out",
}

# Using GPIO.BCM as mode
#GPIO 23 pin16 reboot
#GPIO 25 pin 22 blank screen do not use
GPIO_ACTIONS = {
    4: "module_stats", #GPIO 4
    17: "module_items", #GPIO 14
    27: "module_data", #GPIO 15
#	18:	"knob_1", #GPIO 18 Do Not enable messes with the screen. 
#	18: "knob_2", #GPIO 18 Turns screen off do not use
#	7: "knob_3", #GPIO 7
#	22: "knob_1", #GPIO 22
#	22: "dial_down", #GPIO 22
#	25: "dial_up", #GPIO 25
    24: "knob_2", #GPIO 24
#	25: "knob_3" #GPIO 23
}


MAP_ICONS = {
    "camp": 		pygame.image.load('images/map_icons/camp.png'),
    "factory": 		pygame.image.load('images/map_icons/factory.png'),
    "metro": 		pygame.image.load('images/map_icons/metro.png'),
    "misc": 		pygame.image.load('images/map_icons/misc.png'),
    "monument": 	pygame.image.load('images/map_icons/monument.png'),
    "vault": 		pygame.image.load('images/map_icons/vault.png'),
    "settlement": 	pygame.image.load('images/map_icons/settlement.png'),
    "ruin": 		pygame.image.load('images/map_icons/ruin.png'),
    "cave": 		pygame.image.load('images/map_icons/cave.png'),
    "landmark": 	pygame.image.load('images/map_icons/landmark.png'),
    "city": 		pygame.image.load('images/map_icons/city.png'),
    "office": 		pygame.image.load('images/map_icons/office.png'),
    "sewer": 		pygame.image.load('images/map_icons/sewer.png'),
}

AMENITIES = {
    'pub': 				MAP_ICONS['vault'],
    'nightclub': 		MAP_ICONS['vault'],
    'bar': 				MAP_ICONS['vault'],
    'fast_food': 		MAP_ICONS['sewer'],
#	'cafe': 			MAP_ICONS['sewer'],
#	'drinking_water': 	MAP_ICONS['sewer'],
    'restaurant': 		MAP_ICONS['settlement'],
    'cinema': 			MAP_ICONS['office'],
    'pharmacy': 		MAP_ICONS['office'],
    'school': 			MAP_ICONS['office'],
    'bank': 			MAP_ICONS['monument'],
    'townhall': 		MAP_ICONS['monument'],
#	'bicycle_parking': 	MAP_ICONS['misc'],
#	'place_of_worship': MAP_ICONS['misc'],
#	'theatre': 			MAP_ICONS['misc'],
#	'bus_station': 		MAP_ICONS['misc'],
#	'parking': 			MAP_ICONS['misc'],
#	'fountain': 		MAP_ICONS['misc'],
#	'marketplace': 		MAP_ICONS['misc'],
#	'atm': 				MAP_ICONS['misc'],
}

INVENTORY_OLD = [
"Ranger Sequoia",
"Anti-Materiel Rifle ",
"Deathclaw Gauntlet",
"Flamer",
"NCR dogtag",
".45-70 Gov't(20)",
".44 Magnum(20)",
"Pulse Grenade (2)"
]

# CRT Barrel Distortion Effect
CRT_EFFECT_ENABLED = True
CRT_EFFECT_STRENGTH = 0.05  # 0.0 = no curve, 0.05 = subtle, 0.15 = moderate, 0.25 = strong

# Boot Sequence Configuration
BOOT_SEQUENCE_ENABLED = True
BOOT_CHAR_DELAY = 0.04          # 40ms per character
BOOT_CURSOR_BLINK = 0.5         # 500ms cursor blink interval
BOOT_LINE_PAUSE_BLINKS = 3      # Cursor blinks between lines
BOOT_INITIAL_BLINKS = 3         # Cursor blinks before typing starts
BOOT_SCROLL_SPEED = 300         # Pixels per second for scroll-up
BOOT_SKIP_KEYS = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]

pygame.font.init()
FONTS = {}
for x in range(10, 28):
    FONTS[x] = pygame.font.Font('monofonto.ttf', x)
