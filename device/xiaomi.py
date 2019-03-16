from miio.airpurifier import AirPurifier, OperationMode


__all__ = ['MiAir']


class MiAir(object):
    def __init__(self, ip, token):
        self.device = AirPurifier(ip=ip, token=token)

    @property
    def status(self):
        self.device.discover()
        return self.device.status()

    def be_custom(self, level):
        self.device.set_favorite_level(level)
        self.device.set_mode(OperationMode.Favorite)

    def be_silent(self):
        self.device.set_mode(OperationMode.Silent)

    def be_auto(self):
        self.device.set_mode(OperationMode.Auto)

    def be_turbo(self):
        self.be_custom(16)
