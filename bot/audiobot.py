from kit import *


# 키워드: ['기가지니', '지니야', '친구야', '자기야']
KEYWORD_INDEX = 1


class AudioBot(object):
    def __init__(self, brain):
        self.brain = brain

    def listen(self):
        play_file('wav/glad.wav')
        while True:
            rc = recognize_self(KEYWORD_INDEX)
            if rc == 200:
                print('[AudioBot] waiting your next word')
                print('owo | Meow!')
                text = get_speech_to_text()
                response = self.brain.find_answer(text)
                if response:
                    get_text_to_speech(response)
                else:
                    play_file('wav/dont_know.wav')
                play_file('wav/anything_else.wav')
