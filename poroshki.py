import argparse
import pickle
import random
import re

import requests
import bs4
import re

from rupo.api import Engine
from rupo.settings import RU_STRESS_DEFAULT_MODEL, ZALYZNYAK_DICT, GENERATOR_MODEL_DIR

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.8; rv:45.0) Gecko/20100101 Firefox/46.0'
      }


class Model:
    def __init__(self, random_seed: int=None):
        random.seed(random_seed)
        self.model = None

    def fit(self, filename: str='text', is_dumped: bool=False,
            should_dump: bool=False):
        #  filename следует писать без разрешения файла. если из файла нужно
        #  взять текст, подразумевается расширение .txt
        #  если нужно выгрузить или загрузить файлы pickle, расширение .pickle
        if not is_dumped:
            with open(filename + '.txt', 'r') as file:
                data = file.read()
            dictionary = {}
            txt = re.findall('[А-Яа-яЁё]+[?!.]?', data)
            prev1, prev2 = txt[0], txt[1]  # TODO: bigrams
            for word in txt:
                word = word.lower()
                end = False
                if word[-1] in '.!,?':
                    end = True
                    if word[-1] == ',':
                        word = word[:-1]
                    else:
                        word = word[:-1]# + '.'
                if prev:
                    dictionary[prev][word] = dictionary[prev].get(word, 0) + 1
                dictionary[word] = dictionary.get(word, {})
                if not end:
                    prev = word
                else:
                    prev = ''
            if should_dump:
                with open(filename + '.pickle', 'wb') as dumped:
                    pickle.dump(dictionary, dumped)
        else:
            with open(filename + '.pickle', 'rb') as dumped:
                dictionary = pickle.load(dumped)
        self.model = dictionary
        print(self.model)

    def generate(self, force_quit: int=None):
        #  в аргумент force_quit следует передать число, если нужно ограничить
        #  максимальную возмжную длину предложения. если конец предложения
        #  будет достигнут с меньшим количеством слов, функция вернет его
        #  если за выделенное количество слов предложение не закончится,
        #  функция вернет все накопившиеся до этого слова принудительно.
        if force_quit is None:
            force_quit = float('inf')
        nline = 1
        line2 = None
        syllables = [9, 8, 9]
        ssent = []
        while nline < 4:
            count = syllables[nline - 1]
            sent = []
            prev = random.choice(tuple(self.model.keys()))
            bad = set()
            while count != 0:
                words = self.model[prev]
                words_prob = map(lambda a: (words[a] / len(words), a), words)
                words_prob = sorted(words_prob, reverse=True)
                choice, total = random.random(), 0
                for probability, token in words_prob:
                    total += probability
                    if choice < total:
                        break
                if token not in bad:
                    c = sum([1 if i in 'уеыаоэяию' else 0 for i in token])
                    if count - c >= 0:
                        count -= c
                        sent.append(token)
                        prev = token
                    else:
                        bad.add(token)
            nline += 1
            ssent.append(sent)
        l2 = ssent[1][-1]
        request = requests.get('https://rifme.net/r/{}/1#slogov'.format(l2), headers=headers).text
        dom = bs4.BeautifulSoup(request)
        res = list(filter(lambda a: sum([1 if i in 'уеыаоэяиюё' else 0 for i in a]) == 2, map(lambda a: a.split('"')[1],
                          re.findall('data-w="\w+"', str(dom.findAll('ul', {"class": 'rifmypodryad'})[0])))))
        q = random.random() * len(res)
        word_ = res[int(q)]
        ssent.append([word_])
        print('\n'.join(map(lambda a: ' '.join(a), ssent)))

        # engine = Engine()
        # engine.load(RU_STRESS_DEFAULT_MODEL, ZALYZNYAK_DICT)
        # word_ = str(None)

        # for word_ in self.model.keys():
        #     if sum([1 if i in 'уеыаоэяиюё' else 0 for i in word_]) != 2:
        #         continue
        #     print(l2, word_)
        #     if engine.is_rhyme(l2, word_) and l2 != word_:
        #         break
        """--------------------------------------------------------"""
        # prev = random.choice(tuple(self.model.keys()))
        # end, sent, step = prev[-1] == '.', [prev], 1
        # while not end and step < force_quit:
        #     words = self.model[prev]
        #     words_prob = map(lambda a: (words[a] / len(words), a), words)
        #     words_prob = sorted(words_prob, reverse=True)
        #     choice, total = random.random(), 0
        #     for probability, token in words_prob:
        #         total += probability
        #         if choice < total:
        #             break
        #     sent.append(token)
        #     prev = token
        #     end = token[-1] == '.'
        #     step += 1
        # return ' '.join(sent)


parser = argparse.ArgumentParser(description="Генерация словестных последоват\
                                              ельностей при помощи n-грам")
parser.add_argument('--filename', metavar='filename', type=str, default='text',
                    help='filename следует писать без разрешения \
                    файла. если из файла нужно взять текст, подразумевается \
                    расширение .txt; если нужно выгрузить или загрузить файлы \
                    pickle, расширение .pickle')
parser.add_argument('--seed', metavar='seed', help='Seed для инициализации \
                    ГПСЧ')
parser.add_argument('--should_load', action='store_true',
                    help='Требуется ли загрузить модель из файла')
parser.add_argument('--should_dump', action='store_true',
                    help='Требуется ли выгрузить модель в файл')
parser.add_argument('--force_quit', metavar='force_quit', type=int,
                    help='число, если нужно ограничить максимальную \
                    возмжную длину предложения. если конец предложения будет \
                    достигнут с меньшим количеством слов, функция вернет его. \
                    если за выделенное количество слов предложение не \
                    закончится, функция вернет все накопившиеся до этого \
                    слова принудительно.')

if __name__ == '__main__':
    args = parser.parse_args()
    fname, fq, shl, rnd, shd = (args.filename, args.force_quit,
                                args.should_load, args.seed, args.should_dump)
    fname = '/home/afentev/PycharmProjects/proj/text'
    m = Model(random_seed=rnd)
    m.fit(filename=fname, is_dumped=shl, should_dump=shd)
    m.generate(force_quit=fq)
