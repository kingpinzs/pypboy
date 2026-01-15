"""
Waveform cache system for radio visualization.
Analyzes audio files once and caches the waveform data for fast playback visualization.
"""

import os
import json
import numpy as np
import pygame


class WaveformCache:
    """
    Manages waveform data caching for audio files.
    Analyzes audio once, caches to .waveform files, loads on subsequent plays.
    """

    # Samples per second for cached waveform (50 = 20ms resolution)
    SAMPLES_PER_SECOND = 50

    # Cache file extension
    CACHE_EXT = '.waveform'

    def __init__(self):
        self.cache = {}  # filename -> waveform data

    def get_cache_path(self, audio_path):
        """Get the cache file path for an audio file."""
        return audio_path + self.CACHE_EXT

    def has_cache(self, audio_path):
        """Check if cached waveform exists for audio file."""
        cache_path = self.get_cache_path(audio_path)
        return os.path.exists(cache_path)

    def load_cache(self, audio_path):
        """Load cached waveform data from file."""
        cache_path = self.get_cache_path(audio_path)
        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading waveform cache: {e}")
            return None

    def save_cache(self, audio_path, data):
        """Save waveform data to cache file."""
        cache_path = self.get_cache_path(audio_path)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            print(f"Cached waveform: {cache_path}")
            return True
        except Exception as e:
            print(f"Error saving waveform cache: {e}")
            return False

    def analyze_audio(self, audio_path):
        """
        Analyze audio file and extract waveform envelope.
        Returns dict with duration, sample_rate, and amplitude samples.
        """
        try:
            # Initialize mixer if needed
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

            # Load as Sound to get array access
            sound = pygame.mixer.Sound(audio_path)
            samples = pygame.sndarray.array(sound)

            # Get mixer frequency for timing
            freq, _, stereo = pygame.mixer.get_init()

            # Convert to mono if stereo
            if len(samples.shape) > 1 and samples.shape[1] == 2:
                samples = (samples[:, 0].astype(float) + samples[:, 1].astype(float)) / 2
            else:
                samples = samples.astype(float)

            # Calculate total duration
            total_samples = len(samples)
            duration = total_samples / freq

            # Calculate samples per chunk for our target resolution
            chunk_size = freq // self.SAMPLES_PER_SECOND

            # Extract envelope (max amplitude per chunk)
            envelope = []
            for i in range(0, total_samples, chunk_size):
                chunk = samples[i:i + chunk_size]
                if len(chunk) > 0:
                    # Get peak amplitude (absolute value)
                    peak = np.max(np.abs(chunk))
                    envelope.append(float(peak))

            # Normalize to 0-1 range
            if envelope:
                max_val = max(envelope)
                if max_val > 0:
                    envelope = [v / max_val for v in envelope]

            data = {
                'duration': duration,
                'sample_rate': self.SAMPLES_PER_SECOND,
                'envelope': envelope
            }

            return data

        except Exception as e:
            print(f"Error analyzing audio {audio_path}: {e}")
            return None

    def get_waveform(self, audio_path):
        """
        Get waveform data for audio file.
        Loads from cache if available, otherwise analyzes and caches.
        """
        # Check memory cache first
        if audio_path in self.cache:
            return self.cache[audio_path]

        # Check file cache
        data = self.load_cache(audio_path)
        if data:
            self.cache[audio_path] = data
            return data

        # Analyze and cache
        print(f"Analyzing audio for waveform: {audio_path}")
        data = self.analyze_audio(audio_path)
        if data:
            self.save_cache(audio_path, data)
            self.cache[audio_path] = data
            return data

        return None

    def get_amplitude_at_time(self, audio_path, time_seconds):
        """
        Get the amplitude value at a specific time in the audio.
        Returns 0-1 normalized amplitude, or 0 if not available.
        """
        data = self.get_waveform(audio_path)
        if not data or not data.get('envelope'):
            return 0

        envelope = data['envelope']
        sample_rate = data.get('sample_rate', self.SAMPLES_PER_SECOND)

        # Calculate sample index from time
        index = int(time_seconds * sample_rate)

        # Clamp to valid range
        if index < 0:
            index = 0
        if index >= len(envelope):
            index = len(envelope) - 1

        return envelope[index] if envelope else 0

    def get_amplitude_range(self, audio_path, start_time, end_time, num_points):
        """
        Get a range of amplitude values for visualization.
        Returns list of num_points amplitude values between start and end time.
        """
        data = self.get_waveform(audio_path)
        if not data or not data.get('envelope'):
            return [0] * num_points

        envelope = data['envelope']
        sample_rate = data.get('sample_rate', self.SAMPLES_PER_SECOND)
        duration = data.get('duration', 0)

        # Clamp times to valid range
        start_time = max(0, start_time)
        end_time = min(duration, end_time)

        if end_time <= start_time:
            return [0] * num_points

        # Calculate time step
        time_step = (end_time - start_time) / num_points

        result = []
        for i in range(num_points):
            t = start_time + i * time_step
            index = int(t * sample_rate)
            if 0 <= index < len(envelope):
                result.append(envelope[index])
            else:
                result.append(0)

        return result


# Global cache instance
waveform_cache = WaveformCache()
