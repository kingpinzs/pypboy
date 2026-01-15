"""
Platform detection module for pypboy.

Detects whether running on Raspberry Pi or desktop (x86/x64) and provides
platform-specific configuration.
"""

import platform
import os


class PlatformInfo:
    """Detects and stores platform information for pypboy."""

    PLATFORM_PI = "raspberry_pi"
    PLATFORM_DESKTOP = "desktop"

    def __init__(self):
        self.platform_type = self._detect_platform()
        self.is_raspberry_pi = self.platform_type == self.PLATFORM_PI
        self.is_desktop = self.platform_type == self.PLATFORM_DESKTOP
        self.architecture = platform.machine()  # 'x86_64', 'armv7l', 'aarch64'
        self.gpio_available = False

    def _detect_platform(self):
        """
        Detect whether running on Raspberry Pi or desktop.

        Uses multiple detection methods for reliability across different
        Raspberry Pi OS versions (including Bullseye+).
        """
        # Method 1: /proc/device-tree/model (most reliable on Pi)
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().lower()
                if 'raspberry pi' in model:
                    return self.PLATFORM_PI
        except (FileNotFoundError, PermissionError, IOError):
            pass

        # Method 2: /sys/firmware path (alternative location)
        try:
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                model = f.read().lower()
                if 'raspberry pi' in model:
                    return self.PLATFORM_PI
        except (FileNotFoundError, PermissionError, IOError):
            pass

        # Method 3: Architecture + Pi-specific boot files
        arch = platform.machine().lower()
        if arch in ('armv7l', 'armv6l', 'aarch64'):
            # ARM architecture - check for Pi-specific config files
            if os.path.exists('/boot/config.txt') or os.path.exists('/boot/firmware/config.txt'):
                return self.PLATFORM_PI

        # Method 4: x86/x64 architecture = desktop
        if arch in ('x86_64', 'amd64', 'i386', 'i686'):
            return self.PLATFORM_DESKTOP

        # Default to desktop mode for unknown platforms
        return self.PLATFORM_DESKTOP

    def detect_gpio(self):
        """
        Attempt to initialize GPIO and return success status.

        Returns:
            bool: True if GPIO is available and initialized, False otherwise.
        """
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            self.gpio_available = True
        except (ImportError, RuntimeError, Exception):
            self.gpio_available = False
        return self.gpio_available

    def __repr__(self):
        return (
            f"PlatformInfo(type={self.platform_type}, "
            f"arch={self.architecture}, "
            f"gpio={self.gpio_available})"
        )


# Singleton instance for easy import
PLATFORM = PlatformInfo()
