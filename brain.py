import random
from konlpy.tag import Okt

from helper import load_yaml


class Brain(object):

    def __init__(self):
        self.data = None
        self.groups = {}
        self.triggers = None
        self.qnas = []

        self.load_data()
        self.okt = Okt()

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
        pos = self.okt.pos(sentence, stem=True)
        pos = [p[0] for p in pos]
        return pos

    def check_keywords(self, sentence, keywords, pos=None):
        is_valid = True
        pos = pos or self.to_pos(sentence)

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

    def find_answer(self, sentence):
        if self.triggers is not None:
            if not self.check_keywords(sentence, self.triggers):
                return

        pos = self.to_pos(sentence)
        for qna in self.qnas:
            keywords = qna['keywords']
            if self.check_keywords(sentence, keywords, pos=pos):
                answers = qna['answers']
                if isinstance(answers, list):
                    return random.choice(answers)
                return answers
