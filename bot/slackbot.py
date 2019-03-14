import time


class SlackBot(object):
    def __init__(self, brain, sc):
        self.brain = brain
        self.sc = sc

    @staticmethod
    def is_message(response):
        return response['type'] == 'message' and 'text' in response

    @staticmethod
    def is_from_bot(response):
        return 'bot_id' in response

    def say(self, response):
        answer = self.brain.find_answer(response['text'])
        if answer is None:
            return

        kwargs = {}
        # Required
        kwargs['channel'] = response['channel']
        kwargs['text'] = answer
        # Optional
        kwargs['as_user'] = True
        if 'thread_ts' in response:
            kwargs['thread_ts'] = response['thread_ts']

        self.sc.api_call('chat.postMessage', **kwargs)

    def listen(self):
        while True:
            responses = self.sc.rtm_read()
            for response in responses:
                try:
                    if not self.is_message(response) or self.is_from_bot(response):
                        continue
                    self.say(response)
                except:
                    pass
            time.sleep(1)
