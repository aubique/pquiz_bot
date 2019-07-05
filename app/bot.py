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
        return None
    # Send message with generated keyboard
    bot.send_message(**generate_markup(s))
    # Use UserID as key for the dictionary added to global sessions list
    sessions_dict.update({uid: s})


@bot.message_handler(commands=["add", "edit"])
def new_question(message: types.Message):
    """Controller to start adding a question to the DB"""
    uid = message.chat.id
    s = sessions_dict.pop(uid, None)
    if not s:
        s = core.Session(uid)
        s.is_game_mode_edit = True
        sessions_dict.update({uid: s})
    bot.send_message(uid, s.fill_question(None, first=True))


@bot.message_handler(func=lambda messsage: True, content_types=["text"])
def get_reply(message: types.Message):
    """Controller to handle the response typed by the user"""
    uid = message.chat.id
    s = sessions_dict.pop(uid, None)
    reply = message.text
    # If there is no session existing in the global list
    if not s:
        bot.send_message(uid, config.WELCOME)
        return None
    # Game mode: edit
    if s.is_game_mode_edit:
        msg = s.fill_question(reply)
        # In case fill_question loop isn't over we commit back session
        if msg:
            bot.send_message(uid, msg)
            return sessions_dict.update({uid: s})
        return bot.send_message(uid, config.WELCOME)
    # Game mode: verification
    s.finish(reply)
    # If the given response is correct
    if s.is_matched:
        bot.reply_to(
            message,
            config.RIGHT,
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return None
    else:
        bot.reply_to(
            message,
            config.WRONG,
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return sessions_dict.update({uid: s})


if __name__ == "__main__":
    app.run()
