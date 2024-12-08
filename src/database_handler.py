import sqlite3
import json
from typing import List
from src.constants import MOBMENTOR_DB_FILE_NAME, MOBMENTOR_DB_SCRIPT_PATH
from src.constants import PUPIL_ROLE_TEXT, TEACHER_ROLE_TEXT

class DatabaseHandler():
    def __init__(self) -> None:
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.fill_db()

    def connect(self) -> None:
        self.conn = sqlite3.connect(MOBMENTOR_DB_FILE_NAME)
        self.cursor = self.conn.cursor()

    def disconnect(self) -> None:
        self.conn.close()

    def create_tables(self) -> None:
        with open(MOBMENTOR_DB_SCRIPT_PATH, 'r',
                encoding='utf-8') as f:
            sql_script = f.read()
        self.cursor.executescript(sql_script)
        self.conn.commit()

    def fill_db(self) -> None:
        for role_id, role_meaning in enumerate([PUPIL_ROLE_TEXT, TEACHER_ROLE_TEXT]):
            self.cursor.execute('''
            INSERT OR IGNORE INTO UserRoles(role_id, role_meaning)
            VALUES (?, ?)
            ''', (role_id, role_meaning,))


        self.conn.commit()


    def user_exist(self, user_name: str, role: int, psswd=None) ->  sqlite3.Row:
        if psswd == None:
             self.cursor.execute('''
                SELECT *
                FROM Users
                WHERE user_name = ? AND role_id = ?
            ''', (user_name, role,))
        else:
            self.cursor.execute('''
                SELECT *
                FROM Users
                WHERE user_name = ? AND role_id = ? AND psswd = ?
            ''', (user_name, role, psswd,))
        return self.cursor.fetchone()


    def get_role_id(self, role: str) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT role_id
            FROM UserRoles
            WHERE role_meaning = ?
        ''', (role,))
        return self.cursor.fetchone()


    def add_new_pupil(self, user_name: str) -> None:
        role_id = self.get_role_id(PUPIL_ROLE_TEXT)[0]
        self.cursor.execute('''
           INSERT INTO Users(user_name, role_id)
           VALUES (?, ?)
        ''', (user_name, role_id,))
        self.conn.commit()


    def add_new_teacher(self, user_name: str, psswd: str) -> None:
        role_id = self.get_role_id(TEACHER_ROLE_TEXT)[0]
        self.cursor.execute('''
           INSERT OR REPLACE INTO Users(user_name, role_id, psswd)
           VALUES (?, ?, ?)
        ''', (user_name, role_id, psswd,))
        self.conn.commit()


    def change_teacher_password(self, user_name: str, psswd: str) -> None:
        role_id = self.get_role_id(TEACHER_ROLE_TEXT)[0]
        self.cursor.execute('''
           UPDATE Users
           SET psswd = ?
           WHERE user_name = ? AND role_id = ?
        ''', (psswd, user_name, role_id,))
        self.conn.commit()


    def add_new_module(self, module_name: str, module_descr: str) -> None:
        self.cursor.execute('''
           INSERT INTO Modules(module_name, module_descr)
           VALUES (?, ?)
        ''', (module_name, module_descr,))
        self.conn.commit()


    def add_new_topic(self, module_id: int, topic_name: str, topic_text: str) -> None:
        self.cursor.execute('''
            SELECT COUNT(*)
            FROM Topics
            WHERE module_id=?;
        ''', (module_id,))
        topics_number = self.cursor.fetchone()[0]

        self.cursor.execute('''
           INSERT INTO Topics(module_id, topic_id, topic_name, topic_text)
           VALUES (?, ?, ?, ?)
        ''', (module_id, topics_number + 1, topic_name, topic_text,))
        self.conn.commit()


    def update_module(self, module_id: int, module_name: str, module_descr: str) -> None:
        self.cursor.execute('''
           UPDATE Modules
           SET module_name=?, module_descr=?
           WHERE module_id=?
        ''', (module_name, module_descr, module_id))
        self.conn.commit()


    def update_topic(self, module_id: int, topic_id: int, topic_name: str, topic_text: str) -> None:
        self.cursor.execute('''
           UPDATE Topics
           SET topic_name=?, topic_text=?
           WHERE module_id=? AND topic_id=?
        ''', (topic_name, topic_text, module_id, topic_id))
        self.conn.commit()


    def delete_module(self, module_id: int) -> None:
        self.cursor.execute('''
           DELETE FROM Modules
           WHERE module_id=?
        ''', (module_id,))
        self.conn.commit()


    def delete_topic(self, module_id: int, topic_id: int) -> None:
        self.cursor.execute('''
           DELETE FROM Topics
           WHERE module_id=? AND topic_id=?
        ''', (module_id, topic_id,))
        self.conn.commit()


    def get_modules_list(self) -> List[sqlite3.Row]:
        self.cursor.execute('''
            SELECT module_id, module_name
            FROM Modules
        ''')
        return self.cursor.fetchall()


    def get_module_name(self, module_id: int) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT module_name
            FROM Modules
            WHERE module_id = ?
        ''', (module_id,))
        return self.cursor.fetchone()


    def get_module(self, module_id: int) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT module_name, module_descr
            FROM Modules
            WHERE module_id = ?
        ''', (module_id,))
        return self.cursor.fetchone()


    def get_topics_list(self, module_id: int) -> List[sqlite3.Row]:
        self.cursor.execute('''
            SELECT Topics.topic_id, Topics.topic_name
            FROM Topics
            JOIN Modules ON Topics.module_id = Modules.module_id
            WHERE Modules.module_id = ?
        ''', (module_id,))
        return self.cursor.fetchall()


    def get_topic(self, module_id: int, topic_id: int) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT *
            FROM TopicsView
            WHERE module_id = ? AND topic_id = ?
        ''', (module_id, topic_id,))
        return self.cursor.fetchone()



    def get_question_text(self, question_id: int) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT question_text
            FROM Questions
            WHERE question_id = ?
        ''', (question_id,))
        return self.cursor.fetchone()


    def get_questions_by_topic(self, module_id: int, topic_id: int) -> List[sqlite3.Row]:
        self.cursor.execute('''
            SELECT question_id, question_text
            FROM Questions
            WHERE module_id = ? AND topic_id = ? AND question_answer_text IS NOT NULL AND question_answer_text != ''
        ''', (module_id, topic_id,))
        return self.cursor.fetchall()


    def get_questions_by_user(self, user_name: int) -> List[sqlite3.Row]:
        self.cursor.execute('''
            SELECT *
            FROM Questions
            WHERE user_name = ?
        ''', (user_name,))
        return self.cursor.fetchall()


    def get_questions_without_answer(self: int) -> List[sqlite3.Row]:
        self.cursor.execute('''
            SELECT question_id, module_id, topic_id, question_text
            FROM Questions
            WHERE question_answer_text IS NULL OR question_answer_text = ''
        ''')
        return self.cursor.fetchall()


    def get_question_answer(self, module_id: int, topic_id: int, question_id: int) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT question_answer_text
            FROM Questions
            WHERE module_id = ? AND topic_id = ? AND question_id = ?
        ''', (module_id, topic_id, question_id,))
        return self.cursor.fetchone()


    def get_question_user(self, question_id: int) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT user_name
            FROM Questions
            WHERE question_id = ?
        ''', (question_id,))
        return self.cursor.fetchone()


    def add_question(self, module_id: int, topic_id: int, user_name: str, question_text: str) -> None:
        self.cursor.execute('''
            INSERT INTO Questions(
                module_id, topic_id, user_name, question_text
            )
            VALUES (?, ?, ?, ?)
        ''', (module_id, topic_id, user_name, question_text,))
        self.conn.commit()


    def delete_question(self, question_id: int) -> None:
        self.cursor.execute('''
            DELETE FROM Questions
            WHERE question_id = ?
        ''', (question_id,))
        self.conn.commit()


    def answer_question(self, question_id: int, answer_text: str) -> None:
        self.cursor.execute('''
            UPDATE Questions
            SET question_answer_text = ?
            WHERE question_id = ?
            ''', (answer_text, question_id,))
        self.conn.commit()


database_handler = DatabaseHandler()
