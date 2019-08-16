#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: core.py
# Quiz Bot: Game core (Model)

import data
from config import ENGLISH as DEFAULT_LANGUAGE
from random import shuffle, randint


class Ticket(object):
    """
    Class containing information of single question instance
    """

    def __init__(self, database: data.QuestionsDB):
        self.questions_db = database
        self.question_id: int = None
        self.question: str = None
        self.correct_answer: str = None
        self.answers: list = None
        self.correct_answer_pos: int = None
        self.is_matched: bool = False

    def load_from_db(self, question_id: int):
        """
        Load data to the Ticket object from the Questions
        :param question_id: Question ID in the
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

    def save_to_db(self):
        """
        Save properties of Ticket instance to the Questions
        """
        properties = (self.question, self.correct_answer, *self.answers)
        print(properties)
        self.questions_db.insert_row(*properties)

    def set_properties(self, question, correct, *answers):
        """
        Set properties of the Ticket from the extracted tmp list
        """
        self.question = question
        self.correct_answer = correct
        self.answers = list(answers)


class Session(object):
    """
    Operational User Session class that represents Model component
    """

    def __init__(self, user_id: int):
        self.is_game_mode_edit: bool = False
        self.is_game_mode_lang: bool = False
        self.ldb = data.UserInfoTable()
        self.hdb = data.UserHistoryTable()
        self.qdb = data.QuestionsDB()
        self.uid = user_id
        self.ticket = Ticket(self.qdb)
        self.list_add = list()
        self.iter_add = iter(self.qdb.columns)
        self.language: str = None
        self.load_language()

    def start(self):
        """
        Actions to start the game
        Modify ticket-properties to show them in Controller/View later
        Set game over if there are no more questions to propose
        """
        print("Start as:\t\t%s" % self.uid)
        # Question ID is a verified number of the next question
        question_id = self.__choose_question()
        # If game ran out of questions
        if not question_id:
            # Set the variable that the game is finished for this user
            self.game_over = True
            return None
        # Load data to Ticket-instance and access the  by question ID
        self.ticket.load_from_db(question_id)
        self.game_over = False

    def __choose_question(self) -> int:
        """
        Choose a question ID to propose it as the next question
        Get a random number, verify if it's not listed yet in History
        :return: (int) Question ID for further interaction with
        :return: (None) Quit if history length >= questions length
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
        if self.__qlen > self.__hlen:
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
            "Current answer position:%s"
            % self.ticket.correct_answer_pos
        )
        if (message_text == self.ticket.correct_answer) or (
            message_text == str(self.ticket.correct_answer_pos)
        ):
            self.__update_history()
            self.is_matched = True
        else:
            self.is_matched = False
        print("Is answer correct:\t%s" % self.is_matched)

    def fill_question(self, message_text: str, first: bool = False):
        """
        Process of iteration through the column names to create a ticket
        Step by step add data to the list then fill Ticket object
        :param message_text: Text recieved from the user
        """
        column_name = next(self.iter_add, None)
        if not first:
            self.list_add.append(message_text)
            print("column_name is %s" % column_name)
            if not column_name:
                self.ticket.set_properties(*self.list_add)
                self.ticket.save_to_db()
                self.is_game_mode_edit = False
                return None
        return column_name

    def __update_history(self) -> None:
        """
        Update User History
        Insert UserID and QuestionID to UserHistoryTable
        """
        print("User History  is updated!")
        self.hdb.insert_row(self.uid, self.ticket.question_id)

    def delete_user_history(self) -> None:
        """
        Clear History for this user
        Delete any data related to the user in User History
        """
        print("User History is cleared for %s" % self.uid)
        self.hdb.delete_rows_by_uid(self.uid)

    def load_language(self) -> None:
        """
        Set language from UserInfoTable
        If no language record then pick the default and write it to DB
        """
        self.language: str = self.ldb.get_user_language(self.uid)
        if not self.language:
            self.language = DEFAULT_LANGUAGE
            self.ldb.insert_row(self.uid, self.language)
        print("Language:\t\t%s" % self.language)

    def update_language(self, new_language: str) -> None:
        """
        Set language from user's reply
        Update DB with new language for this user
        """
        self.language = new_language
        self.ldb.update_user_language(self.uid, self.language)
        print("New language:\t\t%s" % self.language)
