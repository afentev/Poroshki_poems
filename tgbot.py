# -*- coding: utf-8 -*-

import pymorphy2
import telebot
from telebot import apihelper
from telebot import types

from poroshki import Model

model = Model()
model.fit()
analyzer = pymorphy2.MorphAnalyzer()

pairs = {'NOUN': 'сущ', 'VERB': 'глагол', 'INFN': 'глагол', 'PRTF': 'прич', 'PRTS': 'прич', 'ADJF': 'прил',
         'ADJS':'прил', 'COMP': 'прил', 'GRND': 'деепр', 'NUMR': 'числ', 'ADVB': 'нар', 'NPRO': 'местоим',
         'PREP': 'предлог', 'CONJ': 'союз', 'PRCL': 'частиц', 'INTJ': 'междом', 'PRED': 'предик'}

russian_pairs = {'Существительное': 'сущ', 'Глагол': 'глагол', 'Причастие': 'прич', 'Деепричастие': 'деепр',
                 'Прилагательное': 'прил', 'Числительное': 'числ', 'Наречие': 'нар', 'Местоимение': 'местоим',
                 'Предлог': 'предлог', 'Союз': 'союз', 'Частица': 'частиц', 'Междометие': 'междом',
                 'Предикатив': 'предик'}

apihelper.proxy = {
  'http': 'socks5://user_271520585:e0rYeNgcZGqA@4adbaf.fckrknbot.club:443',
  'https': 'socks5://user_271520585:e0rYeNgcZGqA@4adbaf.fckrknbot.club:443'
}

bot = telebot.TeleBot('876557094:AAHTU7I54LlCcIZwGbixaLwJM-hV8fV0-8g')

status = {}
rate = {}
improvements = {}


@bot.message_handler(commands=['start', 'more', 'settings', 'help', 'rules'])
def start_message(message):
    print(message)
    sender = str(message.from_user.id)
    status[sender] = None
    command = message.text
    if command in ['/start', '/help']:
        kb = types.ReplyKeyboardMarkup()
        kb.add('/more')
        bot.send_message(message.chat.id, 'Привет! Я - бот, который генерирует порошки\n'
                                          'https://ru.wikipedia.org/wiki/Порошок_(поэзия)\nДля того, чтобы получить '
                                          'порошок, напишите /more. Чтобы изменить настройки, нажмите /settings. '
                                          'Данное сообщение доступно по команде /help', reply_markup=kb)
    elif command == '/more':
        kb = types.InlineKeyboardMarkup()
        poem = model.generate()
        kb.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in [chr(128077), chr(128078)]])
        bot.send_message(sender, poem, reply_markup=kb)
    elif command == '/settings':
        bot.send_message(sender, 'Тут пока еще ничего нет :(')
    elif command == '/rules':
        bot.send_message(sender, 'Правила разметки описаны ниже:')
        bot.send_message(sender, '\n'.join(tuple(map(lambda a: a[1] + ' - ' + a[0].lower(), russian_pairs.items()))))


@bot.callback_query_handler(func=lambda a: True)
def inline(call):
    txt = call.message.text.strip().split('\n')
    data = call.data
    print(call)
    if ord(data) == 128077:
        bot.answer_callback_query(callback_query_id=call.id, text='Спасибо!')
    elif ord(data) == 128078:
        status[call.from_user.id] = 'improvement'
        #bot.answer_callback_query(callback_query_id=call.id, text='Жаль, я буду стараться!')
        new = []
        for i in txt:
            n = []
            for j in i.split():
                n.append(analyzer.parse(j)[0].tag.POS)
            new.append(' '.join(n))
        new = '\n'.join(new)
        for i, j in pairs.items():
            new = new.replace(i, j)
        improvements[call.from_user.id] = new
        kb = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        kb.add(*['Всё правильно', 'Ошибка, сейчас исправлю', 'Отстаньте!'])
        bot.send_message(call.from_user.id, 'Спасибо за замечания! Пожалуйста, проверьте корректность нижеприведенных '
                                            'частей речи в стихе (определенных автоматически)')
        bot.send_message(call.from_user.id, 'Если в них есть ошибки, пришлите ответным сообщением правильный разбор '
                                            '(правила - /rules)')
        bot.send_message(call.from_user.id, 'Вы можете отказаться от этого, нажав соответствующую кнопку',
                         reply_markup=kb)
        bot.send_message(call.from_user.id, new)


@bot.message_handler()
def msg(message):
    text = message.text
    sender = message.from_user.id
    kb = types.ReplyKeyboardMarkup()
    kb.add('/more')
    if text == 'Всё правильно':
        if status.get(sender, None) == 'improvement':
            bot.send_message(sender, 'Спасибо за помощь!', reply_markup=kb)
        else:
            bot.send_message(sender, 'Я вас не понимаю :(', reply_markup=kb)
    elif text == 'Ошибка, сейчас исправлю':
        if status.get(sender, None) in ['improvement', 'self-improvement']:
            bot.send_message(sender, 'Хорошо, жду. Если передумаете, напишите "Отстаньте!"')
            status[sender] = 'self-improvement'
        else:
            bot.send_message(sender, 'Я вас не понимаю :(', reply_markup=kb)
    elif text.replace('!', '').lower() == 'отстаньте':
        bot.send_message(sender, 'Хорошо, ничего страшного!', reply_markup=kb)
        status[sender] = None
    elif status.get(sender, None) in ['improvement', 'self-improvement']:
        text1 = text.split('\n')
        if len(text1) == 4 and len(text1[-1].split()) == 1 and not (set(text.split()) - set(tuple(russian_pairs.values()))):
            bot.send_message(sender, 'Спасибо за помощь!', reply_markup=kb)
            print(text1)
        else:
            bot.send_message(sender, 'Где-то в вашем сообщении допущена ошибка, проверьте еще раз')
    else:
        bot.send_message(sender, 'Я вас не понимаю :(', reply_markup=kb)


bot.polling()
