import time
from miio.airpurifier import AirPurifier, OperationMode


__all__ = ['MiAir']


TTL = 300


def discover_required(func):
    def wrapper(self, *args, **kwargs):
        now = time.time()
        if now - self.last_discovered > TTL:
            self.device.discover()
            self.last_discovered = now
        return func(self, *args, **kwargs)
    return wrapper


class MiAir(object):
    def __init__(self, ip, token):
        self.device = AirPurifier(ip=ip, token=token)
        self.last_discovered = 0

    @property
    @discover_required
    def status(self):
        return self.device.status()

    @discover_required
    def be_custom(self, level):
        self.device.set_favorite_level(level)
        self.device.set_mode(OperationMode.Favorite)

    @discover_required
    def be_silent(self):
        self.device.set_mode(OperationMode.Silent)

    @discover_required
    def be_auto(self):
        self.device.set_mode(OperationMode.Auto)

    @discover_required
    def be_turbo(self):
        self.be_custom(16)
