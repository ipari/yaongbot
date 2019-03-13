import ktkws

from kit import detect


# 키워드: ['기가지니', '지니야', '친구야', '자기야']
KEYWORD_INDEX = 1
KWS_MODEL_PATH = 'ai-makers-kit/data/kwsmodel.pack'


class AudioBot(object):
    def __init__(self):
        pass

    @staticmethod
    def recognize_self():
        ktkws.init(KWS_MODEL_PATH)
        ktkws.start()
        ktkws.set_keyword(KEYWORD_INDEX)
        rc = detect()
        ktkws.stop()
        return rc

    def listen(self):
        rc = self.recognize_self()
        if rc == 200:
            print('Meow!')
