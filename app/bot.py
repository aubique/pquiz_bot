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
REPEAT = False


def generate_markup(answers):
    """Generate and return a keyboard markup"""
    reply_markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    reply_markup.add(*answers)
    return reply_markup


def get_locale(user_id) -> str:
    """Return a proper message according the user's tongue"""
    # TODO: Go for JSON localisation data files
    pass


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
    uid: str = message.chat.id
    s = core.Session(uid)
    s.start()
    # If there are no more questions to ask
    if s.game_over:
        bot.send_message(uid, config.CONGRATS)
        return None
    # Send message with generated keyboard
    bot.send_message(
        chat_id=s.uid,
        text=s.ticket.question,
        reply_markup=generate_markup(s.ticket.answers),
    )
    # Use UserID as key for the dictionary added to global sessions list
    sessions_dict.update({uid: s})


@bot.message_handler(commands=["add"])
def new_question(message: types.Message):
    """Controller to start adding a question to the DB"""
    uid: str = message.chat.id
    s: core.Session = sessions_dict.pop(uid, None)
    if not s:
        s = core.Session(uid)
        s.is_game_mode_edit = True
        sessions_dict.update({uid: s})
    # TODO: Find out way to generate message outside of Model
    bot.send_message(uid, s.fill_question(None, first=True))


@bot.message_handler(commands=["language"])
def change_language(message: types.Message):
    """Controller to change the bot language"""
    uid: str = message.chat.id
    s: core.Session = sessions_dict.pop(uid, None)
    if not s:
        s = core.Session(uid)
    # Set Language change game mode even though REPEATing is allowed
    s.is_game_mode_lang = True
    sessions_dict.update({uid: s})
    bot.send_message(
        chat_id=s.uid,
        text=config.ASK_LANGUAGE_MSG,
        reply_markup=generate_markup((config.ENGLISH, config.RUSSIAN)),
    )


@bot.message_handler(commands=["clear"])
def clear_history(message: types.Message):
    """Controller to clear any questions of the current user"""
    uid: str = message.chat.id
    s: core.Session = sessions_dict.pop(uid, None)
    # If this user has yet to pass any questions
    if not s:
        s = core.Session(uid)
    s.delete_user_history()
    bot.send_message(uid, config.CLEARED)
    bot.send_message(uid, config.WELCOME)


@bot.message_handler(func=lambda messsage: True, content_types=["text"])
def get_reply(message: types.Message):
    """Controller to handle the response typed by the user"""
    uid: str = message.chat.id
    s: core.Session = sessions_dict.pop(uid, None)
    reply = message.text
    # If there is no session existing in the global list
    if not s:
        bot.send_message(uid, config.WELCOME)
        return None
    # Game mode - Language change
    if s.is_game_mode_lang:
        # TODO: Verify the reply by linking possible answers in dict
        s.update_language(reply)
        return bot.send_message(uid, config.LANGUAGE_CHANGED_MSG)
    # Game mode - Adding question
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
        # If you can keep answering the same question
        if REPEAT:
            return sessions_dict.update({uid: s})
        return None


if __name__ == "__main__":
    app.run()
