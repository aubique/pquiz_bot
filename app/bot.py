#/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: bot.py
# Quiz game

import requests
import telebot
from telebot import types
from flask import Flask, request
from flask_sslify import SSLify
import config, core

bot = telebot.TeleBot('{}:{}'.format(config.TOKEN1, config.TOKEN2))
app = Flask(__name__)
sslify = SSLify(app)

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

@bot.message_handler(commands=['game', 'next'])
def show_question(message:types.Message):
    cid = str(message.chat.id)
    quiz = core.load_json(config.JSON_QUIZ)
    # Add a var to the storage in case if it's not initialized
    #storage = core.shelve_callback(cid, core.update_history, str(0))
    # Pick a random number which isn't listed in the message history yet
    random_num = core.shelve_callback(cid, core.choose_question, quiz)
    # If we ran of the questions then there is no random number so we indicitate the end
    print('Returned random number:\t'+str(random_num))
    if random_num is None:
        bot.send_message(int(cid), config.CONGRATS)
        return None
    # Question, correct answer, ticket of answers
    q, ca, t = core.get_ticket_data(quiz, random_num)
    # Enable game mode
    s = core.shelve_callback(cid, core.set_user_game, random_num, ca)
    # Generate markup of the mixed answers
    markup = core.generate_markup(t)
    bot.send_message(int(cid), q, reply_markup=markup)

@bot.message_handler(commands=['start'])
def update_history(message: types.Message):
    pass

@bot.message_handler(func=lambda messsage: True, content_types=['text'])
def get_reply(message: types.Message):
    cid = str(message.chat.id)
    num, ca = core.shelve_callback(cid, core.get_correct)
    # Correct answer exists if game is started and initialized it early
    if ca:
        keyboard_hider = types.ReplyKeyboardRemove()
        # If text is right/wrong hide the keyboard and output a message
        if message.text == ca:
            bot.reply_to(message, config.RIGHT, reply_markup=keyboard_hider)
            core.shelve_callback(cid, core.update_history, str(num))
        else:
            bot.reply_to(message, config.WRONG, reply_markup=keyboard_hider)
        # Finish the game and delete the correct answer shelve
        core.shelve_callback(cid, core.finish_user_game)
    else:
        bot.send_message(int(cid), 'Type /game to start the game')

def main():
    pass

if __name__ == '__main__':
    app.run()
