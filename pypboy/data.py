import xmltodict
import requests
import numpy
from numpy.fft import fft
from math import log10
import math
import pygame
import sys
import json


class Maps(object):

    nodes = {}
    ways = []
    tags = []
    origin = None
    width = 0
    height = 0

    SIG_PLACES = 3
    GRID_SIZE = 0.001

    def __init__(self, *args, **kwargs):
        super(Maps, self).__init__(*args, **kwargs)

    def float_floor_to_precision(self, value, precision):
        for i in range(precision):
            value *= 10
        value = math.floor(value)
        for i in range(precision):
            value /= 10
        return value

    def fetch_grid(self, coords):
        lat = coords[0]
        lng = coords[1]

        return self.fetch_area([
                lat - self.GRID_SIZE,
                lng - self.GRID_SIZE,
                lat + self.GRID_SIZE,
                lng + self.GRID_SIZE
        ])

    def fetch_area(self, bounds):
        self.width = (bounds[2] - bounds[0]) / 2
        self.height = (bounds[3] - bounds[1]) / 2
        self.origin = (
                bounds[0] + self.width,
                bounds[1] + self.height
        )
        
        url = "http://www.openstreetmap.org/api/0.6/map?bbox=%f,%f,%f,%f" % (
                        bounds[0],
                        bounds[1],
                        bounds[2],
                        bounds[3]
                )

        print("[Fetching maps... (%f, %f) to (%f, %f)]" % (
                        bounds[0],
                        bounds[1],
                        bounds[2],
                        bounds[3]
                ))
        while True:
            try:
                response = requests.get(url)
            except:
                pass
            else:
                break
        map_data = response.text.encode('UTF-8')
        #Write to cache file
        f = open("map.cache", "w")
        f.write(str(map_data))
        f.close()
        self.display_map(map_data)
    
    def load_map_coordinates(self, coords, range):
        return self.load_map((
                coords[0] - range,
                coords[1] - range,
                coords[0] + range,
                coords[1] + range
        ))
    
    def load_map(self, bounds):
        self.width = (bounds[2] - bounds[0]) / 2
        self.height = (bounds[3] - bounds[1]) / 2
        self.origin = (
                bounds[0] + self.width,
                bounds[1] + self.height
        )
        with open('map.cache', 'r') as mapcache:
            map_data = mapcache.read()
        self.display_map(map_data)
            
    def display_map(self, map_data):
        osm_dict = xmltodict.parse(map_data)
        try:
            for node in osm_dict['osm']['node']:
                self.nodes[node['@id']] = node
                if 'tag' in node:
                    for tag in node['tag']:
                        try:
                            #Named Amenities
                            if tag["@k"] == "name":
                                for tag2 in node['tag']:
                                    if tag2["@k"] == "amenity":
                                        amenity = tag2["@v"]
                                self.tags.append((float(node['@lat']), float(node['@lon']), tag["@v"], amenity))
                            #Personal Addresses - Removed
                            if tag["@k"] == "addr:housenumber":
                                   for t2 in node['tag']:
                                           if t2["@k"] == "addr:street":
                                                   self.tags.append((float(node['@lat']), float(node['@lon']),tag["@v"]+" "+t2["@v"]))
                                                   print(tag["@v"])
                            if tag["@k"] == "tiger:county":
                                print(tag["@v"])
                        except Exception:
                            pass

            for way in osm_dict['osm']['way']:
                waypoints = []
                for node_id in way['nd']:
                    node = self.nodes[node_id['@ref']]
                    waypoints.append((float(node['@lat']), float(node['@lon'])))
                self.ways.append(waypoints)
        except Exception:
            _, err, _ = sys.exc_info()
            print(err)
    

    def fetch_by_coordinate(self, coords, range):
        return self.fetch_area((
                coords[0] - range,
                coords[1] - range,
                coords[0] + range,
                coords[1] + range
        ))

    def transpose_ways(self, dimensions, offset, flip_y=True):
        width = dimensions[0]
        height = dimensions[1]
        w_coef = width / self.width / 2
        h_coef = height / self.height / 2
        transways = []
        for way in self.ways:
            transway = []
            for waypoint in way:
                lat = waypoint[1] - self.origin[0]
                lng = waypoint[0] - self.origin[1]
                wp = [
                        (lat * w_coef) + offset[0],
                        (lng * h_coef) + offset[1]
                ]
                if flip_y:
                    wp[1] *= -1
                    wp[1] += offset[1] * 2
                transway.append(wp)
            transways.append(transway)
        return transways

    def transpose_tags(self, dimensions, offset, flip_y=True):
        width = dimensions[0]
        height = dimensions[1]
        w_coef = width / self.width / 2
        h_coef = height / self.height / 2
        transtags = []
        for tag in self.tags:
            lat = tag[1] - self.origin[0]
            lng = tag[0] - self.origin[1]
            # Some tags have 4 elements (lat, lon, name, amenity), some have only 3
            amenity = tag[3] if len(tag) > 3 else None
            wp = [
                            tag[2],
                            (lat * w_coef) + offset[0],
                            (lng * h_coef) + offset[1],
                            amenity
            ]
            if flip_y:
                wp[2] *= -1
                wp[2] += offset[1] * 2
            transtags.append(wp)
        return transtags


class GeoLocation:
    """Reverse geocoding using Nominatim API with caching."""

    CACHE_FILE = "location.cache"
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
    USER_AGENT = "PypBoy/1.0 (Pip-Boy Emulator)"
    TIMEOUT = 5
    DEFAULT_AREA = "Local Area"

    def get_area_name(self, longitude, latitude):
        """Get area name from cache or API."""
        cached = self._read_cache(longitude, latitude)
        if cached:
            return cached

        area_name = self._fetch_from_api(longitude, latitude)
        if area_name != self.DEFAULT_AREA:
            self._write_cache(longitude, latitude, area_name)
        return area_name

    def _fetch_from_api(self, longitude, latitude):
        """Fetch area name from Nominatim."""
        try:
            response = requests.get(
                self.NOMINATIM_URL,
                params={"lat": latitude, "lon": longitude, "format": "json", "addressdetails": 1},
                headers={"User-Agent": self.USER_AGENT},
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            # Priority: city > town > village > suburb > municipality > county
            address = data.get("address", {})
            for field in ["city", "town", "village", "suburb", "municipality", "county"]:
                if field in address:
                    return address[field]
            return self.DEFAULT_AREA
        except Exception as e:
            print(f"[GeoLocation] API error: {e}")
            return self.DEFAULT_AREA

    def _read_cache(self, longitude, latitude):
        """Read cached area name if coordinates match."""
        try:
            with open(self.CACHE_FILE, "r") as f:
                cache = json.load(f)
            if (abs(cache.get("longitude", 0) - longitude) < 0.001 and
                abs(cache.get("latitude", 0) - latitude) < 0.001):
                return cache.get("area_name")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return None

    def _write_cache(self, longitude, latitude, area_name):
        """Write area name to cache file."""
        try:
            with open(self.CACHE_FILE, "w") as f:
                json.dump({"longitude": longitude, "latitude": latitude, "area_name": area_name}, f)
        except Exception as e:
            print(f"[GeoLocation] Cache write error: {e}")


class SoundSpectrum: 
    """ 
    Obtain the spectrum in a time interval from a sound file. 
    """ 

    left = None 
    right = None 
    
    def __init__(self, filename, force_mono=False): 
        """ 
        Create a new SoundSpectrum instance given the filename of 
        a sound file pygame can read. If the sound is stereo, two 
        spectra are available. Optionally mono can be forced. 
        """ 
        # Get playback frequency 
        nu_play, format, stereo = pygame.mixer.get_init() 
        self.nu_play = 1./nu_play 
        self.format = format 
        self.stereo = stereo 

        # Load sound and convert to array(s) 
        sound = pygame.mixer.Sound(filename)
        a = pygame.sndarray.array(sound) 
        a = numpy.array(a) 
        if stereo: 
            if force_mono: 
                self.stereo = 0 
                self.left = (a[:,0] + a[:,1])*0.5 
            else: 
                self.left = a[:,0] 
                self.right = a[:,1] 
        else: 
            self.left = a 

    def get(self, data, start, stop): 
        """ 
        Return spectrum of given data, between start and stop 
        time in seconds. 
        """ 
        duration = stop-start 
        # Filter data 
        start = int(start/self.nu_play) 
        stop = int(stop/self.nu_play) 
        N = stop - start 
        data = data[start:stop] 

        # Get frequencies 
        frequency = numpy.arange(N/2)/duration 

        # Calculate spectrum 
        spectrum = fft(data)[1:1+N/2] 
        power = (spectrum).real 

        return frequency, power 

    def get_left(self, start, stop): 
        """ 
        Return spectrum of the left stereo channel between 
        start and stop times in seconds. 
        """ 
        return self.get(self.left, start, stop) 

    def get_right(self, start, stop): 
        """ 
        Return spectrum of the left stereo channel between 
        start and stop times in seconds. 
        """ 
        return self.get(self.right, start, stop) 

    def get_mono(self, start, stop): 
        """ 
        Return mono spectrum between start and stop times in seconds. 
        Note: this only works if sound was loaded as mono or mono 
        was forced. 
        """ 
        return self.get(self.left, start, stop) 

class LogSpectrum(SoundSpectrum): 
    """ 
    A SoundSpectrum where the spectrum is divided into 
    logarithmic bins and the logarithm of the power is 
    returned. 
    """ 

    def __init__(self, filename, force_mono=False, bins=20, start=1e2, stop=1e4): 
        """ 
        Create a new LogSpectrum instance given the filename of 
        a sound file pygame can read. If the sound is stereo, two 
        spectra are available. Optionally mono can be forced. 
        The number of spectral bins as well as the frequency range 
        can be specified. 
        """ 
        SoundSpectrum.__init__(self, filename, force_mono=force_mono) 
        start = log10(start) 
        stop = log10(stop) 
        step = (stop - start)/bins 
        self.bins = 10**numpy.arange(start, stop+step, step) 

    def get(self, data, start, stop): 
        """ 
        Return spectrum of given data, between start and stop 
        time in seconds. Spectrum is given as the log of the 
        power in logatithmically equally sized bins. 
        """ 
        f, p = SoundSpectrum.get(self, data, start, stop) 
        bins = self.bins 
        length = len(bins) 
        result = numpy.zeros(length) 
        ind = numpy.searchsorted(bins, f) 
        for i,j in zip(ind, p): 
            if i < length: 
                result[i] += j 
        return bins, result 