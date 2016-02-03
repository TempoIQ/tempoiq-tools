import tempoiq.session
from os import path
import getopt
import sys
import itertools
from tempoiq.protocol.device import Device
from tempoiq.protocol.sensor import Sensor
from tempoiq.protocol.encoder import CreateEncoder
import datetime
import json

DEFAULT_START = datetime.datetime(2000, 1, 1)
DEFAULT_END = datetime.datetime(2018, 1, 1)
DEFAULT_FILTERS = []
# Add device filters like:
#DEFAULT_FILTERS.append(Device.attributes['region'] == 'north')

class Exporter(object):
    def __init__(self, opts, path='.'):
        cli = tempoiq.session.get_session(opts['host'],
                                          opts['key'],
                                          opts['secret'])
        self.client = cli
        self.devices = []
        self.path = path
        if 'resume_device' in opts:
            self.resume_device = opts['resume_device']
        else:
            self.resume_device = None

    def export(self):
        if self.resume_device is None:
            self.export_devices()

        self.export_datapoints(start=DEFAULT_START, end=DEFAULT_END)

    def export_devices(self):
        req = self.client.query(Device)
        for filt in DEFAULT_FILTERS:
            req = req.filter(filt)
        response = req.read()

        if response.successful != tempoiq.response.SUCCESS:
            print("Error reading devices {}-{}"
                  .format(response.status, response.reason))
            return

        for device in response.data:
            self.devices.append(device)

        with open(self.file_in_path('devices.json'), 'w') as outfile:
            json.dump(self.devices, outfile, default=CreateEncoder().default)

    def export_datapoints(self, start, end):
        if not self.devices:
            with open(self.file_in_path('devices.json')) as infile:
                self.devices = json.load(infile)

        outfile = open(self.file_in_path('datapoints.tsv'), 'a')

        started = (self.resume_device is None)
        if started:
            print("Exporting data from {} devices".format(len(self.devices)))

        for device in self.devices:
            try:
                deviceKey = device.key
            except AttributeError:
                deviceKey = device["key"]

            if not started:
                if deviceKey == self.resume_device:
                    print("resuming with device {}".format(deviceKey))
                    started = True
                else:
                    continue

            for (dev, sen, ts, val) in self._read_device(start, end, deviceKey):
                outfile.write('{}\t{}\t{}\t{}\n'
                              .format(dev, sen, ts.isoformat(), val))
        outfile.close()

    def file_in_path(self, filename):
        return path.join(self.path, filename)

    def _read_device(self, start, end, deviceKey):
        res = self.client.query(Sensor) \
                         .filter(Device.key == deviceKey) \
                         .read(start=start, end=end)
        if res.successful != tempoiq.response.SUCCESS:
            print("Error reading data from device {}: {}-{}"
                  .format(deviceKey, res.status, res.reason))
            return

        for row in res.data:
            for ((device, sensor), value) in row:
                yield (device, sensor, row.timestamp, value)


def main(argv):
    creds = {}
    try:
        opts, args = getopt.getopt(argv, "n:k:s:r:")
    except getopt.GetoptError:
        print('export.py -n <backend> -k <key> -s <secret> -r <device>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-k":
            creds['key'] = arg
        elif opt == "-s":
            creds['secret'] = arg
        elif opt == "-n":
            creds['host'] = arg
        elif opt == "-r":
            creds['resume_device'] = arg

    if not creds['host'].startswith('http'):
        creds['host'] = 'https://' + creds['host']

    exporter = Exporter(creds)
    exporter.export()

if __name__ == "__main__":
    main(sys.argv[1:])
