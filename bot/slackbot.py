import time


class SlackBot(object):
    def __init__(self, sc):
        self.sc = sc

    def listen(self):
        while True:
            time.sleep(1)
