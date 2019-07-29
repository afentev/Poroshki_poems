# -*- coding: utf-8 -*-

import telebot
from telebot import apihelper
from telebot import types

from poroshki import Model

model = Model()
model.fit()

apihelper.proxy = {
  'http': 'socks5://user_22222222:XXXXXXXXXXXXXX@4adbaf.fckrknbot.club:443',
  'https': 'socks5://user_2222222222:XXXXXXXXXXXXXX@4adbaf.fckrknbot.club:443'
}

bot = telebot.TeleBot('222222:XXXXXXXXXXXXXXX-YYYYY-ZZ')

status = {}
last = {}


@bot.message_handler(commands=['start', 'more', 'settings', 'help'])
def start_message(message):
    sender = message.from_user.id
    command = message.text
    if command in ['/start', '/help']:
        bot.send_message(message.chat.id, 'Привет! Я - бот, который генерирует порошки\n'
                                          'https://ru.wikipedia.org/wiki/Порошок_(поэзия)\nДля того, чтобы получить '
                                          'порошок, напишите /more. Чтобы изменить настройки, нажмите /settings. '
                                          'Данное сообщение доступно по команде /help')
    elif command == '/more':
        kb = types.InlineKeyboardMarkup()
        kb.add(*[types.InlineKeyboardButton(text=name, callback_data=name) for name in [chr(128077), chr(128078)]])
        poem = model.generate()
        bot.send_message(message.chat.id, poem, reply_markup=kb)
        last[sender] = last.get(sender, [])
        last[sender].append(poem)
        if len(last) > 5:
            del last[0]
    elif command == '/settings':
        pass


@bot.callback_query_handler(func=lambda a: True)
def inline(call):
    if ord(call.data) == 128077:
        bot.answer_callback_query(callback_query_id=call.id, text='Спасибо!')
    elif ord(call.data) == 128078:
        bot.answer_callback_query(callback_query_id=call.id, text='Жаль, я буду стараться!')


bot.polling()
