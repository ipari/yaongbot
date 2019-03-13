import time

from audiobot import AudioBot

__all__ = [b'Bot']


class Bot(object):
    def __init__(self, sc):
        self.sc = sc
        self.audiobot = AudioBot()

    def listen(self):
        while True:
            self.audiobot.listen()
            time.sleep(1)
