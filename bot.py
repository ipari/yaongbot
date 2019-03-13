import time


__all__ = [b'Bot']


class Bot(object):
    def __init__(self, sc):
        self.sc = sc

    def listen(self):
        while True:
            print('Yaong!')
            time.sleep(1)
