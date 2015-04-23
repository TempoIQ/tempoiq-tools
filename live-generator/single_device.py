#!/usr/bin/env python

from generator.generator import DataGenerator
import sys
from select import select
import datetime
import pytz
import os
import optparse


def main():
    parser = optparse.OptionParser()
    parser.add_option("-p", "--period", dest="period", default=2, help="How often to log data (seconds)")
    parser.add_option("-d", "--device", dest="device", help="Device key")

    (options, args) = parser.parse_args()
    if not options.device:
        parser.error("Please specify a device key with -d")

    creds = creds_from_env()
    if not creds:
        print("TempoIQ credentials not found in environment variables TIQ_KEY, TIQ_SECRET, TIQ_HOST")
        sys.exit(1)

    utc = pytz.timezone('UTC')
    gen = DataGenerator(device=options.device, creds=creds)

    print("Type u<ENTER> to increase a sensor's value by 2.0.")
    print("Type d<ENTER> to decrease by 2.0.")
    while True:
        ts = datetime.datetime.now(utc)
        points = gen.write_points(ts)

        print(ts.strftime("%Y-%m-%d %H:%M:%S") + " " + value_str(points))
        canRead, _, _ = select([sys.stdin], [], [], float(options.period))
        if canRead:
            data = sys.stdin.readline().lower()

            if data.startswith("u"):
                sen, val = gen.offset_first_sensor(2.0)
                print("*** Increase sensor {} to {} ***".format(sen, val))
            elif data.startswith("d"):
                sen, val = gen.offset_first_sensor(-2.0)
                print("*** Decrease sensor {} to {} ***".format(sen, val))


def creds_from_env():
    creds = {}
    try:
        creds['key'] = os.environ['TIQ_KEY']
        creds['secret'] = os.environ['TIQ_SECRET']
        creds['host'] = os.environ['TIQ_HOST']
    except KeyError:
        return None

    if "://" not in creds['host']:
        creds['host'] = "https://" + creds['host']

    return creds


def value_str(dic):
    string = ""
    for key, value in dic.iteritems():
        string += "{}: {:.2f}, ".format(key, value)
    return string


if __name__ == '__main__':
    main()
