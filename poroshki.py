import argparse
import pickle
import random
import math

import requests
import bs4
import re

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
            prev = ''
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

    def generating_procedure(self):
        nline = 1
        syllables = [9, 8, 9]
        ssent = []
        counter = 1
        while nline < 4:
            count = syllables[nline - 1]
            sent = []
            prev = random.choice(tuple(self.model.keys()))
            bad = set()
            while count != 0:
                token = None
                if counter > 60:
                    return self.generating_procedure()
                counter += 1
                words = self.model[prev]
                words_prob = map(lambda a: (words[a] / len(words), a), words)
                words_prob = sorted(words_prob, reverse=True)
                choice, total = random.random(), 0
                for probability, token in words_prob:
                    total += probability
                    if choice < total:
                        break
                if token is None:
                    return self.generating_procedure()
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
        return ssent

    def generate(self, force_quit: int=None):
        #  в аргумент force_quit следует передать число, если нужно ограничить
        #  максимальную возмжную длину предложения. если конец предложения
        #  будет достигнут с меньшим количеством слов, функция вернет его
        #  если за выделенное количество слов предложение не закончится,
        #  функция вернет все накопившиеся до этого слова принудительно.
        ssent = self.generating_procedure()
        l2 = ssent[1][-1]
        request = requests.get('https://rifme.net/r/{}/1#slogov'.format(l2), headers=headers).text
        dom = bs4.BeautifulSoup(request)
        res = list(filter(lambda a: sum([1 if i in 'уеыаоэяиюё' else 0 for i in a]) == 2, map(lambda a: a.split('"')[1],
                          re.findall('data-w="\w+"', str(dom.findAll('ul', {"class": 'rifmypodryad'})[0])))))
        const = 0.75  # 0 < const ⩽ 1. Регулирует производную в распределении. Чем ближе к единице, тем меньше производная (слова становятся более равновероятными)
        y1 = (const - 1) / (pow(const, len(res)) - 1)
        n = int(math.log(random.random() / y1, const)) + 1
        word_ = res[n if n < len(res) else 0]
        ssent.append([word_])
        return '\n'.join(map(lambda a: ' '.join(a), ssent))


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
    print(m.generate(force_quit=fq))
