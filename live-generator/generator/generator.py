from tempoiq.session import get_session
from tempoiq.protocol import Device, Sensor
import random


class DataGenerator:
    """Class to generate realistic-looking sensor data for a single device"""
    def __init__(self, device, creds):
        self.client = get_session(creds['host'], creds['key'], creds['secret'])
        self.lv_cache = {}

        result = self.client.query(Device).filter(Device.key == device).read()

        if not result.data:
            print("ERROR: No device found!")
            return

        self.device = iter(result.data).next()

    def write_points(self, timestamp):
        device_data = {}

        for sens in self.device.sensors:
            value = self.next_value(sens.key)
            device_data[sens.key] = [{'t': timestamp, 'v': value}]

        self.client.write({self.device.key: device_data})

        return self.lv_cache

    def get_nominal(self, key):
        """Nominal values range from 18-51"""
        return ((hash(key) % 12) + 6.0) * 3

    def next_value(self, key):
        prob = random.random()
        oldval = self.lv_cache.get(key, self.get_nominal(key))

        # Stddev ranges from 0.1-0.6
        stddev = ((hash(key) % 11) + 2.0) * 0.05
        value = oldval + random.normalvariate(0, stddev)

        self.lv_cache[key] = value
        return value

    def offset_first_sensor(self, offset):
        key = self.device.sensors[0].key
        value = self.next_value(key) + offset   # make sure there's an entry in lv_cache
        self.lv_cache[key] = value
        return (key, value)

