#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: bot.py
# Quiz game: Telegram (Controller/View)

import telebot
from telebot import types
from flask import Flask, request, abort
from flask_sslify import SSLify
import core
import config

bot = telebot.TeleBot("{}:{}".format(config.TOKEN1, config.TOKEN2))
app = Flask(__name__)
sslify = SSLify(app)
sessions_dict = {}


def generate_markup(session: core.Session) -> dict:
    """Generate keyboard markup to show question and answers"""
    answers = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    answers.add(*session.ticket.answers)
    return {
        "chat_id": session.uid,
        "text": session.ticket.question,
        "reply_markup": answers,
    }


@app.route("/", methods=["POST", "GET"])
def webhook():
    """Update on GET/POST requests"""
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        abort(403)

<<<<<<< HEAD

@bot.message_handler(commands=["game", "next"])
def show_question(message: types.Message):
    """Controller to start the game session"""
    uid = message.chat.id
    # TODO: Singleton __new__() wrapper to check instances by uid
    s = core.Session(uid)
    # Session start main method
    s.start()
    # If there are no more questions to ask
    if s.game_over:
        bot.send_message(uid, config.CONGRATS)
=======
@bot.message_handler(commands=['game', 'next'])
def show_question(message:types.Message):
    cid = str(message.chat.id)
    quiz = core.load_json(config.JSON_QUIZ)
    # Pick a random number which isn't listed in the message history yet
    random_num = core.shelve_callback(cid, core.choose_question, quiz)
    # If we ran of the questions then there is no random number so we indicitate the end
    print('Returned random number:\t'+str(random_num))
    if random_num is None:
        bot.send_message(int(cid), config.CONGRATS)
>>>>>>> 5db9be8685e1375afddd48ec79dd5a473ef9bc99
        return None
    # Send message with generated keyboard
    bot.send_message(**generate_markup(s))
    # Use UserID as key for the dictionary added to global sessions list
    sessions_dict.update({uid: s})

<<<<<<< HEAD
=======
@bot.message_handler(commands=['add'])
def update_history(message: types.Message):
    cid = str(message.chat.id)
    core.shelve_callback(cid, core.finish_user_game)
    bot.send_message(int(cid), 'Enter here your question')
    core.shelve_callback(cid, core.set_game_editor)
>>>>>>> 5db9be8685e1375afddd48ec79dd5a473ef9bc99

@bot.message_handler(func=lambda messsage: True, content_types=["text"])
def get_reply(message: types.Message):
<<<<<<< HEAD
    """Controller to finish the game session"""
    uid = message.chat.id
    s = sessions_dict.pop(uid, None)
    # If there a session existing in the global list
    if not s:
        bot.send_message(uid, config.WELCOME)
        return None
    s.finish(message.text)
    # If the given response is correct
    if s.is_matched:
        bot.reply_to(
            message,
            config.RIGHT,
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        sessions_dict.update({uid: s})
        bot.reply_to(
            message,
            config.WRONG,
            reply_markup=types.ReplyKeyboardRemove(),
        )
=======
    cid = str(message.chat.id)
    msg_text = message.text
    num, ca = core.shelve_callback(cid, core.get_correct)
    # Correct answer exists if game is started and initialized it early
    if ca:
        keyboard_hider = types.ReplyKeyboardRemove()
        # If text is right/wrong hide the keyboard and output a message
        if msg_text == ca:
            bot.reply_to(message, config.RIGHT, reply_markup=keyboard_hider)
            core.shelve_callback(cid, core.update_history, str(num))
        else:
            bot.reply_to(message, config.WRONG, reply_markup=keyboard_hider)
        # Finish the game and delete the correct answer shelve
        core.shelve_callback(cid, core.finish_user_game)
    else:
        s = core.shelve_callback(cid, core.recieve_question_data, msg_text)
        if s:
            bot.send_message(int(cid), core.get_question_mark(s))
            print('EDITED STORAGE:\t{}'.format(s))
        else:
            bot.send_message(int(cid), 'Type /game to start the game')
>>>>>>> 5db9be8685e1375afddd48ec79dd5a473ef9bc99


if __name__ == "__main__":
    app.run()
