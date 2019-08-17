#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: data.py
# Quiz Bot: Database implementation

import sqlite3
import config


class SQLiteCursor(object):
    """
    Simple context manager for database based on SQLite3
    It commits everything at exit
    """

    def __init__(self, path):
        self.__path = path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.__path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()


class GenericDB(object):
    """
    Parent database class for interaction with SQLite3 DB
    """

    def __init__(self, row_dict):
        """
        Execute query to create a new table if not exists
        :param row_dict: Dictionary to query
        """
        with SQLiteCursor(self._fname) as c:
            c.execute(
                self.Utility.generate_create_query(
                    self._table, row_dict
                )
            )

    def insert_row(self, row_dict: dict) -> None:
        """
        Execute query to insert a row into the instance table
        :param row_dict: Dictionary to query
        """
        with SQLiteCursor(self._fname) as c:
            c.execute(
                self.Utility.generate_insert_query(
                    self._table, row_dict
                )
            )

    def count_all_rows(self) -> int:
        """
        Count a number of rows in the table
        :return: (int) Number of row in the whole table
        """
        with SQLiteCursor(self._fname) as c:
            rows = c.execute(
                self.Utility.generate_select_all(self._table)
            ).fetchall()
        return len(rows)

    def select_all_rows(self) -> int:
        """
        Select all rows in the current DB
        :return: (list) List of row-tuples
        """
        with SQLiteCursor(self._fname) as c:
            rows = c.execute(
                self.Utility.generate_select_all(self._table)
            ).fetchall()
        return rows

    def search_rows_by_arg(self, attribute, value) -> list:
        """
        Find multiple rows by the given attribute
        :param attribute: Attribute of column for search
        :param value: Value for search
        :return: (list) Row-tuples where values of attributes match
        """
        with SQLiteCursor(self._fname) as c:
            rows = c.execute(
                self.Utility.generate_select_by(
                    self._table, attribute, value
                )
            ).fetchall()
        return rows

    def delete_rows_by_arg(self, attribute: str, value: str) -> None:
        """
        Delete multiple rows by the given attribute
        :param attribute: Name of column to delete
        :param value: Value of the column that gets deleted
        """
        with SQLiteCursor(self._fname) as c:
            c.execute(
                self.Utility.generate_delete_by(
                    self._table, attribute, value
                )
            )

    def search_cols_by_arg(
        self, column: str, attribute: str, value: str
    ) -> list:
        """
        Search multiple rows of the certain column by attribute
        :param column: Column that we select for filtering
        :param attribute: Attribute of column for search
        :param value: Value for search
        :return: (list) Row-tuples matched by value, filtered by column
        """
        values_list = list()
        with SQLiteCursor(self._fname) as c:
            # We get a list of tuples filtered by column
            rows = c.execute(
                self.Utility.generate_column_select_by(
                    self._table, column, attribute, value
                )
            ).fetchall()
        # Extract 1st item of each tuple to the new list
        values_list.append([values_tuple[0] for values_tuple in rows])
        return values_list[0]

    def search_col_by_arg(
        self, column: str, attribute: str, value: str
    ) -> str:
        """
        Find one row of the certain column by attribute
        :param column: Column that we select for filtering
        :param attribute: Attribute of column for search
        :param value: Value for search
        :return: (str) Row matched by value, filtered by column
        """
        rows = self.search_cols_by_arg(column, attribute, value)
        if rows:
            return rows[0]

    def search_row_by_id(self, value) -> tuple:
        """
        Search a row by primary key ID
        :param value: Value of primary key ID
        :return: (tuple) Row found by ID value
        """
        with SQLiteCursor(self._fname) as c:
            row = c.execute(
                self.Utility.generate_select_by(
                    self._table, "ID", value
                )
            ).fetchone()
        return row

    def update_row_by_arg(
        self, row_dict: dict, attribute: str, value: str) -> None:
        """
        Execute query to update a row by argument and its value
        :param row_dict: Dictionary of columns to set/update
        :param attribute: Column name for condition
        :param value: Value of column for condition
        """
        with SQLiteCursor(self._fname) as c:
            c.execute(
                self.Utility.generate_update_query(
                    self._table, row_dict, attribute, value
                )
            )


    class Utility:
        """
        Collection of static methods
        """

        @staticmethod
        def generate_create_query(table, kwargs) -> str:
            """
            Generate a SQL query to create table with certain args
            :param table: Name of the table
            :param kwargs: Dictionary with keys and its' types
            :return: (str) Formatted SQL query string
            """
            string = "CREATE TABLE IF NOT EXISTS %s" % table
            string += "(id integer primary key"
            string += "".join(
                [",{} {}".format(k, t) for k, t in kwargs.items()]
            )
            string += ")"
            return string

        @staticmethod
        def generate_insert_query(table: str, kwargs: dict) -> str:
            """
            Generate SQL query to insert various arguments
            :param table: Table name
            :param kwargs: Dictionary with keys and values
            :return: (str) Formatted SQL insert query string
            """
            string1 = "INSERT INTO %s (" % table
            string2 = "VALUES ("
            for k, v in kwargs.items():
                string1 += "%s," % k
                string2 += "'%s'," % v
            string1 = string1[:-1] + ") "
            string2 = string2[:-1] + ")"
            return string1 + string2

        @staticmethod
        def generate_select_all(table: str) -> str:
            """
            Generate SQL query to select all rows
            :param table: Table name
            :return: (str) Formatted SQL select query string
            """
            string = "SELECT * FROM %s" % table
            return string

        @staticmethod
        def generate_select_by(table, attribute, value) -> str:
            """
            Generate SQL query to select a row by the given attribute
            """
            return "SELECT * FROM {} WHERE {} = '{}'".format(
                table, attribute, value
            )

        @staticmethod
        def generate_column_select_by(
            table, column, attribute, value
        ) -> str:
            """
            Generate SQL query to select certain columns of rows
            Search by the given argument and its value
            :return: (str) Formatted SQL select query string
            """
            return "SELECT {} FROM {} WHERE {} = '{}'".format(
                column, table, attribute, value
            )

        @staticmethod
        def generate_delete_by(table, attribute, value) -> str:
            """
            Generate SQL query to delete rows by the given attribute
            """
            return "DELETE FROM {} WHERE {} = '{}'".format(
                table, attribute, value
            )

        @staticmethod
        def generate_update_query(
            table: str, kwargs: dict, attribute: str, value: str) -> str:
            """
            Generate SQL query to update row by attribute
            Stetement: UPDATE table SET column=value WHERE condition
            :param table:
            :param kwargs:
            :param attribute:
            :param value:
            :return: (str) Formatted SQL update query string
            """
            string = "UPDATE %s SET" % table
            string += ",".join(
                [" {} = '{}'".format(k, t) for k, t in kwargs.items()]
            )
            string += " WHERE {} = {}".format(attribute, value)
            print(string)
            return string

        @staticmethod
        def generate_dict(columns: tuple, values: tuple) -> dict:
            """
            Generate a dictionary with columns as key and values
            :param columns: Column names
            :param values: Values tuple
            :return: (dict) Dictionary of associated columns and values
            """
            return dict(zip(columns, values))


class QuestionsDB(GenericDB):
    """
    Child database class to interact with Questions database
    """

    def __init__(self):
        self._fname = config.QUESTIONS_DBPATH
        self._table = config.QUESTIONS_TABLE
        self.columns = (
            config.QUESTION,
            config.CORRECT,
            config.ANSWER1,
            config.ANSWER2,
            config.ANSWER3,
        )
        values = (
            config.TYPE_TEXT,
            config.TYPE_TEXT,
            config.TYPE_TEXT,
            config.TYPE_TEXT,
            config.TYPE_TEXT,
        )
        row = super().Utility.generate_dict(self.columns, values)
        super().__init__(row)

    def insert_row(self, *args: tuple) -> None:
        """
        Sent generated dictionary to Parent DB
        """
        dic = super().Utility.generate_dict(self.columns, args)
        return super().insert_row(dic)


class UserHistoryTable(GenericDB):
    """
    Child database class to interact with Questions History data
    It uses the same DB as UserInfoTable located at HISTORY_DBPATH
    """

    def __init__(self):
        self._fname = config.HISTORY_DBPATH
        self._table = config.USER_HISTORY_TABLE
        self.columns = (config.USER_ID, config.QUESTION_ID)
        values = (config.TYPE_INTEGER, config.TYPE_INTEGER)
        row = super().Utility.generate_dict(self.columns, values)
        super().__init__(row)

    def search_rows_by_uid(self, user_id: int) -> list:
        return super().search_rows_by_arg(config.USER_ID, user_id)

    def delete_rows_by_uid(self, user_id: int) -> None:
        return super().delete_rows_by_arg(config.USER_ID, user_id)

    def search_qnum_by_uid(self, user_id: int) -> list:
        return super().search_cols_by_arg(
            config.QUESTION_ID, config.USER_ID, user_id
        )

    def insert_row(self, *args: tuple) -> None:
        dic = super().Utility.generate_dict(self.columns, args)
        return super().insert_row(dic)


class UserInfoTable(GenericDB):
    """
    Child database class to interact with Language User data
    It uses the same DB as UserHistoryTable located at HISTORY_DBPATH
    """

    def __init__(self):
        self._fname = config.HISTORY_DBPATH
        self._table = config.USER_LANGUAGE_TABLE
        self.columns = (config.USER_ID, config.LANGUAGE_CODE)
        values = (config.TYPE_INTEGER, config.TYPE_TEXT)
        row = super().Utility.generate_dict(self.columns, values)
        super().__init__(row)

    def delete_rows_by_uid(self, user_id: int) -> None:
        return super().delete_rows_by_arg(config.USER_ID, user_id)

    def get_user_language(self, user_id: int) -> str:
        """
        Find a language record
        Search language_code column for this UserID
        :param user_id: User ID
        :return: (str) Language code (ru/en/fr)
        :return: (None) If list of searched columns is empty
        """
        return super().search_col_by_arg(
            config.LANGUAGE_CODE, config.USER_ID, user_id
        )

    def update_user_language(self, user_id: int, language: str) -> None:
        """
        Update language record in UserInfoTable of History DB
        Get a SQL queue string from static method and execute it
        :param user_id: User ID
        :param language: New language code meant to be written in DB
        """
        return super().update_row_by_arg(
            {config.LANGUAGE_CODE: language}, config.USER_ID, user_id
        )

    def insert_row(self, *args: tuple) -> None:
        dic = super().Utility.generate_dict(self.columns, args)
        return super().insert_row(dic)
