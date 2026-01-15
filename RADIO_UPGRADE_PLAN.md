# Radio Upgrade Plan - Fallout 3/New Vegas Style

## Overview
This document describes the radio module upgrade to match the Fallout 3/New Vegas Pip-Boy 3000 interface with:
1. **OFF option** at the top of the station list
2. **Real-time waveform visualization** on the right side

## Reference
Based on Fallout: New Vegas Pip-Boy radio screen:
- Station list on left with selection marker
- Continuous waveform line (amplitude over time) on right
- Horizontal axis with tick marks (time ruler at bottom)
- Vertical axis with tick marks (amplitude scale on right)

## Implementation Summary

### Files Created
| File | Description |
|------|-------------|
| `pypboy/modules/data/waveform.py` | RadioWaveform Entity class - animated waveform visualization |
| `pypboy/modules/data/waveform_cache.py` | WaveformCache class - audio analysis and caching system |
| `sounds/radio/*/*.waveform` | Pre-cached waveform data for all audio files |

### Files Modified
| File | Changes |
|------|---------|
| `pypboy/modules/data/entities.py` | Added `RadioOff` class for turning radio off |
| `pypboy/modules/data/radio.py` | Integrated OFF option and waveform visualization |
| `config.py` | Added waveform configuration constants |

## Screen Layout

```
+------------------------------------------------------------------+
|  DATA --------------------------------- Radio    01.15.26 12:30  |
+------------------------------------------------------------------+
|                                                                   |
|   OFF                            +---------------------------+    |
|   Galaxy News Radio              |                      |    |    |
|   Diamond City Radio             |     ~~~waveform~~~   |    |    |
|   Enclave Radio                  |    /\    /\    /\    |    |    |
|   Institute Radio                |   /  \  /  \  /  \   |    |    |
|   Minutemen Radio                |  /    \/    \/    \  |    |    |
|   Vault 101 Radio                |                      |    |    |
|   Violin Radio                   |  |__|__|__|__|__|__| |    |    |
|   F3 Radio                       +---------------------------+    |
|                                                                   |
+------------------------------------------------------------------+
|   Local Map   World Map   Quests   Misc   [Radio]                |
+------------------------------------------------------------------+

Menu: x=4, y=60, width=200
Waveform: x=220, y=60, width=240, height=180
```

## Component Details

### RadioOff Class (entities.py)
```python
class RadioOff:
    """Pseudo-station for turning radio OFF."""
    label = "OFF"

    def stop(self):
        pygame.mixer.music.stop()
```

### RadioWaveform Class (waveform.py)
- Extends `game.Entity` (240x180 pixels)
- Animated sine wave when playing
- Flat line when stopped/OFF
- Axis tick marks matching Fallout aesthetic
- Colors: Primary green (95, 255, 177), Secondary green (60, 180, 120)

### Radio Module Changes (radio.py)
- OFF added as first station (index 0)
- Waveform created before menu (initialization order)
- `select_station()` handles OFF vs station selection
- `render()` drives waveform animation

## Configuration (config.py)
```python
RADIO_WAVEFORM_WIDTH = 240
RADIO_WAVEFORM_HEIGHT = 180
RADIO_WAVEFORM_X = 220
RADIO_WAVEFORM_Y = 60
RADIO_WAVEFORM_COLOR = (95, 255, 177)
RADIO_WAVEFORM_AXIS_COLOR = (60, 180, 120)
```

## Technical Notes

### Waveform Animation (Real Audio Data)
The waveform now displays **real audio data** from the playing song:
- Audio files are analyzed once and cached to `.waveform` files
- Cache files store amplitude envelope at 50 samples/second
- Cached data is committed to git so no runtime analysis needed
- `pygame.mixer.music.get_pos()` syncs display to current playback position

### Waveform Cache System
- **Cache file format**: JSON with duration, sample_rate, and envelope array
- **Cache location**: Same directory as audio file with `.waveform` extension
- **Auto-generation**: New files are automatically analyzed on first play
- **Pre-cached**: All existing audio files have cache files committed

### Station List
1. OFF (index 0) - Stops music immediately
2. Galaxy News Radio
3. Diamond City Radio
4. Enclave Radio
5. Institute Radio
6. Minutemen Radio
7. Vault 101 Radio
8. Violin Radio
9. F3 Radio

## Testing

### Verification Steps
1. Run `python main.py`
2. Navigate to DATA > Radio tab (F3 key, then navigate to Radio)
3. Verify:
   - [ ] OFF appears at top of station list
   - [ ] Selecting OFF stops music immediately
   - [ ] Waveform shows flat line when OFF
   - [ ] Selecting a station starts playback
   - [ ] Waveform animates when playing
   - [ ] Axis tick marks visible (bottom and right)
   - [ ] Song end triggers next track, waveform continues

### Controls
- **F3**: Switch to DATA module
- **1-5 or Up/Down**: Navigate submodules to Radio
- **Up/Down arrows**: Navigate station list
- **Enter/Click**: Select station

## Future Enhancements
- Real-time audio FFT analysis (requires different audio handling)
- Current song title display
- Signal strength indicator
- Volume control visualization
