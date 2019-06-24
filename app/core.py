#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: core.py
# Quiz Bot: Game core (Model)

import data
from random import shuffle, randint

<<<<<<< HEAD
=======
QST_INDEX = 0
LAST_INDEX = 4

def get_hid(user_id):
    """
    Get an ID for shelve of the history message
    :param user_id: User ID to convert
    :return: (str) Converted UID for history message
    """
    return user_id + 'hist'
>>>>>>> 5db9be8685e1375afddd48ec79dd5a473ef9bc99

class Ticket(object):
    """
    Class containing information of single question instance
    """

<<<<<<< HEAD
    def __init__(self, database: data.QuestionsDB):
        self.questions_db = database
        self.question_id: int = None
        self.question: str = None
        self.correct_answer: str = None
        self.answers: list = None
        self.correct_answer_pos: int = None
        self.is_matched: bool = False
=======
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
>>>>>>> 5db9be8685e1375afddd48ec79dd5a473ef9bc99

    def load(self, question_id: int):
        """
        Load data to the Ticket object from the Questions DB
        :param question_id: Question ID in the DB
        """
        row: tuple = self.questions_db.search_row_by_id(question_id)
        # row = (id, question, correct_answer, *answers)
        self.question_id = row[0]
        self.question = row[1]
        self.correct_answer = row[2]
        # Merge correct answer and extracted tuple of answers
        self.answers = [self.correct_answer, *row[3:]]
        shuffle(self.answers)
        # Position is a list index augmented once
        self.correct_answer_pos = (
            self.answers.index(self.correct_answer) + 1
        )


class Session(object):
    """
    Operational class
    """

    def __init__(self, user_id: int):
        self.hdb = data.HistoryDB()
        self.qdb = data.QuestionsDB()
        self.uid = user_id
        self.ticket = Ticket(self.qdb)

    def start(self):
        """
        Actions to start the game
        Modify ticket-properties to show them in Controller/View later
        Set game over if there are no more questions to propose
        """
        print("Start as:\t\t%s" % self.uid)
        # Question ID is a verified number of the next question
        question_id = self.choose_question()
        # If game ran out of questions
        if not question_id:
            # Set the variable that the game is finished for this user
            self.game_over = True
            return None
        # Load data to Ticket-instance and access the DB by question ID
        self.ticket.load(question_id)
        self.game_over = False

<<<<<<< HEAD
    def choose_question(self):
        """
        Choose a question ID to propose it as the next question
        Verify if it's not listed in User History DB
        :return: (int) Question row ID for further interaction with DB
        :return: (None) If history length >= questions length
        """
        self.__history: list = self.hdb.search_qnum_by_uid(self.uid)
        print("History:\t\t%s" % self.__history)
        # Calculate a user history length
        self.__hlen: int = len(self.__history)
        # Questions list length
        self.__qlen: int = len(self.qdb.select_all_rows())
        # Question left = Question length - History length
        self.__qleft: int = self.__qlen - self.__hlen
        print("Question left:\t\t%s" % self.__qleft)
        # If there is atleast 1 question left to propose it keeps going
        if self.__qleft:
            while True:
                rand_index: int = randint(1, self.__qlen)
                # If question ID is not listed in history yet then break
                if rand_index not in self.__history:
                    print("Rand number:\t\t%s" % rand_index)
                    return rand_index

    def finish(self, message_text: str):
        """
        Actions to finish the game
        Verify whether the answer is correct and set is_matched
        :param message_text: Text recieved from the user
        """
        print("Finish as:\t\t%s" % self.uid)
        print(
            "Right answer position:\t%s"
            % self.ticket.correct_answer_pos
        )
        if (message_text == self.ticket.correct_answer) or (
            message_text == str(self.ticket.correct_answer_pos)
        ):
            self.update_history()
            self.is_matched = True
        else:
            self.is_matched = False
        print("Is answer correct:\t%s" % self.is_matched)

    def update_history(self):
        """
        Update User History DB
        Insert user ID and question ID to the database
        """
        print("User History DB is updated!")
        self.hdb.insert_row(self.uid, self.ticket.question_id)
=======
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
>>>>>>> 5db9be8685e1375afddd48ec79dd5a473ef9bc99
