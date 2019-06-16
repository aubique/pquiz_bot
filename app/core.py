#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: core.py
# Quiz game core

import json
import re
import shelve
from random import sample, randint
from telebot import types
import config

QST_INDEX = 0
LAST_INDEX = 4

def get_hid(user_id):
    """
    Get an ID for shelve of the history message
    :param user_id: User ID to convert
    :return: (str) Converted UID for history message
    """
    return user_id + 'hist'

def get_cid(user_id):
    """
    Get an ID for shelve of the correct answer
    :param user_id: User ID to convert
    :return: (str) Converted UID for correct answer
    """
    return user_id + 'corr'

def get_eid(user_id):
    """
    """
    return user_id + 'edit'

def load_json(filename=config.JSON_QUIZ):
    """
    Open file and deserialize content to a python object
    JSON-array = Python-list, according to the conversion table
    :param func: prefix describing a function of the open file
    :return: (list) List of dictionaries
    """
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(data):
    """
    Save JSON data to the file
    :param func: appointed function of the file
    :param data: JSON data
    """
    filename = 'quiz'
    with open('db_{}.json'.format(filename), 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        return True

def update_history(chat_id, storage, data):
    """
    Update a history of the questions already passed
    Update an existing shelve of create a new one
    :param chat_id: original UserID to associate a key of the Shelve DB
    :param data: Index of the question to write down
    :return: (list) Return the updated Shelve DB
    """
    hid = get_hid(chat_id)
    print('QNumber:\t\t'+str(data))
    try:
        history = storage[hid]
        history.append(data)
        storage[hid] = history
    except KeyError:
        print('\nupdate_history(): KEY ERROR\n')
        storage[hid] = list(data)
    finally:
        print('Storage and its type:\t'.format(type(storage[hid])),(storage[hid]))
        return storage

def shelve_callback(chat_id, callback_func, *cb_args):
    """
    Within the function body call the function recieved in the params
    Pass the parameters to the callback and return its value
    :param chat_id: original UserID
    :callback_func: A function to callback
    :param *cb_args: Stuff for the CallBack function
    :return: (obj) Pass the object returned by the called function
    """
    with shelve.open(config.SHELVE_FILE) as storage:
        #if cb_args: return callback_func(chat_id, storage, *cb_args)
        #else: return callback_func(chat_id, storage)
        return callback_func(chat_id, storage, *cb_args)

def choose_question(chat_id, storage, quiz):
    """
    Choose a random number to propose for new question
    To get a number it takes an interval determined by the quiz length
    :param chat_id: original UserID
    :param storage: Shelve DB instance
    :param quiz: JSON data of the full quiz
    :return: (int) Return a random number / None if KeyError
    """
    hid = get_hid(chat_id)
    try:
        history = storage[hid]
        history_len = len(history)
    except KeyError:
        print('\nchoose_question()\tKEY ERROR\n')
        history = list()
        history_len = 0
    quiz_len = len(quiz)
    questions_left = quiz_len - history_len
    print('QUESTIONS left:\t\t({}q)'.format(questions_left))
    if questions_left:
        i = 0
        while True:
            i += 1
            num = randint(0, quiz_len-1)
            #print('RandInt(0, {}-1) = {}'.format(quiz_len, num))
            #print('WHILE iteration:\ti={}'.format(i))
            if not str(num) in history:
                return num

def get_ticket_data(quiz, question_number):
    """
    Extract the question ticket and cut it into pieces
    :param quiz: JSON quiz data
    :param question_number: Number of the question
    :return: Strings of question and right answer, list of mixed answers
    """
    ticket = quiz[question_number]
    question = ticket['Q']
    correct_answer = ticket['A'][0]
    ticket['A'] = sample(ticket['A'], len(ticket['A']))
    return question, correct_answer, ticket['A']

def set_user_game(chat_id, storage, question_index, correct_answer):
    """
    Enable game mode
    Initialize correct answer shelve
    :param chat_id: original UserID
    :param storage: Shelve DB
    """
    storage[get_cid(chat_id)] = [question_index, correct_answer]
    print('Game Mode: Enabled')
    return storage

def finish_user_game(chat_id, storage):
    """
    Disable game mode
    Delete the correct answer shelve
    :param chat_id: original UserID
    """
    print('Game Mode: Disabled')
    try:
        del storage[get_cid(chat_id)]
    except KeyError:
        return None

def get_correct(chat_id, storage):
    """
    Get a correct answer from the correct answer shelve
    If '/game' command hasn't been sent except KeyError and return Nothing
    :param chat_id: original UserID
    :param storage: Shelve DB
    """
    cid = get_cid(chat_id)
    try:
        correct = storage[cid]
        return correct
    # In case '/game' hasn't been sent and game isn't started yet
    except KeyError:
        return [None, None]

def generate_markup(answers):
    """
    Generate keyboard markup to send
    :param answers: mixed answer list
    :return: (telebot.types.ReplyKeyboardMarkup) Return keyboard layout of answers
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(*answers)
    #[markup.add(i) for i in *answers]
    return markup

def set_game_editor(chat_id, storage):
    """
    Initialize question editor shelve
    Prepare it for recieving data by list.append function
    :param chat_id: User ID
    """
    print('Game Mode: Editor')
    eid = get_eid(chat_id)
    storage[eid] = ['-1']
    return storage

def recieve_question_data(chat_id, storage, text):
    """
    Recieve and write to the shelve the question data
    :param chat_id: User ID
    :param storage: #TODO
    :param text: #TODO
    :return: (list) #TODO / (None)
    """
    eid = get_eid(chat_id)
    storage_edit = storage[eid]
    iteration = int(storage_edit[QST_INDEX])
    storage_edit[QST_INDEX] = str(iteration+1)
    storage[eid] = storage_edit + [text]
    if iteration < LAST_INDEX:
        return storage[eid]
    else:
        return None

def get_question_mark(storage):
    i = int(storage[QST_INDEX])
    if i == 0:
        return 'Enter the correct answer'
    elif i < LAST_INDEX:
        return 'Enter another answer'
    else:
        return 'You completed the question'
