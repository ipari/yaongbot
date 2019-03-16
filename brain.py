import jpype
import random
from konlpy.tag import Okt

from hand import Hand
from helper import load_yaml


POS = {
    'number': 'Number',
    'noun': 'Noun'
}


class Brain(object):

    def __init__(self):
        self.groups = {}
        self.triggers = None
        self.qnas = []
        self.okt = Okt()

        self.load_data()
        self.hand = Hand()

    def process_group(self, keyword, allow_group=True):
        if not keyword.startswith('group:'):
            return keyword

        if not allow_group:
            print('group 에서는 group 을 사용할 수 없습니다.')
            return

        group_key = keyword.split(':')[1]
        try:
            return self.groups[group_key]
        except KeyError:
            print('groups 에서 {}를 찾을 수 없습니다.', group_key)

    def process_keywords(self, keywords, allow_group=True):
        if not isinstance(keywords, list):
            keywords = [keyword.strip() for keyword in keywords.split(',')]
        keywords = [self.process_group(keyword, allow_group) for keyword in keywords]
        return keywords

    def load_data(self):
        data = load_yaml('data.yml')

        if data['groups'] is not None:
            for group, keywords in data['groups'].items():
                data['groups'][group] = self.process_keywords(keywords, allow_group=False)
        self.groups = data['groups']

        if data['triggers'] is not None:
            data['triggers'] = self.process_keywords(data['triggers'])
        self.triggers = data['triggers']

        for qna in data['qnas']:
            qna['keywords'] = self.process_keywords(qna['keywords'])
        self.qnas = data['qnas']

    def to_pos(self, sentence):
        # 멀티스레드에서 JVM 부를 때 발생하는 SIGSEGV 에러 해결.
        jpype.attachThreadToJVM()

        pos = self.okt.pos(sentence, stem=True)
        return pos

    def check_keywords(self, sentence, keywords, pos=None):
        is_valid = True
        pos = pos or self.to_pos(sentence)
        pos = [p[0] for p in pos]

        for keyword in keywords:
            if isinstance(keyword, list):
                if any(word in pos for word in keyword):
                    continue
                if any(word in sentence for word in keyword):
                    continue
                is_valid = False
            else:
                if keyword not in pos and keyword not in sentence:
                    is_valid = False
        return is_valid

    @staticmethod
    def process_params(params, pos):
        if not isinstance(params, list):
            params = [param.strip() for param in params.split(',')]
        args = [[s for s, t in pos if t == POS[param]][0] for param in params]
        return args

    def find_answer(self, sentence):
        print('[Brain] find answer')

        pos = self.to_pos(sentence)
        print('    | {}'.format(pos))

        if self.triggers is not None:
            if not self.check_keywords(sentence, self.triggers, pos=pos):
                print('>>> | no trigger in text'.format(sentence))
                return

        for qna in self.qnas:
            keywords = qna['keywords']
            if not self.check_keywords(sentence, keywords, pos=pos):
                continue

            answers = qna['answers']
            if not isinstance(answers, list):
                answers = [answers]
            answer = random.choice(answers)

            actions = qna.get('actions')
            if actions:
                results = []
                for action in actions:
                    name = action.get('device')
                    method = action.get('action')
                    params = action.get('params', [])
                    args = self.process_params(params, pos)
                    print('    | action: {}.{}({})'.format(name, method, ', '.join(args)))

                    result = self.hand.do_action(name, method, args)
                    if isinstance(result, tuple):
                        results += result
                    else:
                        results.append(result)
                answer = answer.format(*results)
            print('>>> | "{}"'.format(answer))
            return answer
        print('>>> | no match answer')
        return
