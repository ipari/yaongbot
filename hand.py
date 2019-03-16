from six import viewitems, viewvalues

from device.xiaomi import *
from helper import load_yaml

ROOM_INFO_KEYS = ['temperature', 'humidity', 'aqi']
XIAOMI = {
    'airpurifier': MiAir
}


class Hand(object):
    def __init__(self):
        self.devices = {}
        self.load_devices()

    def load_devices(self):
        brands = load_yaml('device.yml')
        xiaomi_devices = brands.get('xiaomi', {})
        self.set_xiaomi_device(xiaomi_devices)

    def set_xiaomi_device(self, devices):
        for name, info in viewitems(devices):
            if 'type' not in info or not info['type']:
                print('ERR | <{}> require "type"'.format(name))
                continue

            ip = info.get('ip')
            token = info.get('token')
            if not (ip and token):
                print('ERR | <{}> require "ip", "token"'.format(name))
            device = XIAOMI[info['type']](ip=ip, token=token)
            self.devices[name] = device

    def get_room_info(self):
        info = {key: None for key in ROOM_INFO_KEYS}
        for device in viewvalues(self.devices):
            for key in ROOM_INFO_KEYS:
                try:
                    value = getattr(device.status, key)
                except AttributeError:
                    continue
                if value is not None:
                    info[key] = value
            if all(value is not None for value in viewvalues(info)):
                return info
        return info
