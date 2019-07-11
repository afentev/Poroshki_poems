import argparse
import pickle
import random
import re

from rupo.api import Engine
from rupo.settings import RU_STRESS_DEFAULT_MODEL, ZALYZNYAK_DICT, GENERATOR_MODEL_DIR


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
            prev = ''
            for word in re.findall('[А-Яа-яЁё]+[?!.]?', data):
                word = word.lower()
                end = False
                if word[-1] in '.!,?':
                    end = True
                    if word[-1] == ',':
                        word = word[:-1]
                    else:
                        word = word[:-1] + '.'
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
        syllables = [9, 8, 9, 2]
        while nline < 4:
            count = syllables[nline - 1]

        prev = random.choice(tuple(self.model.keys()))
        end, sent, step = prev[-1] == '.', [prev], 1
        while not end and step < force_quit:
            words = self.model[prev]
            words_prob = map(lambda a: (words[a] / len(words), a), words)
            words_prob = sorted(words_prob, reverse=True)
            choice, total = random.random(), 0
            for probability, token in words_prob:
                total += probability
                if choice < total:
                    break
            sent.append(token)
            prev = token
            end = token[-1] == '.'
            step += 1
        return ' '.join(sent)


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
    m = Model(random_seed=rnd)
    m.fit(filename=fname, is_dumped=shl, should_dump=shd)
    print(m.generate(force_quit=fq))
