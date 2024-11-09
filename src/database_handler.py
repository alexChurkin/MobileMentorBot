import sqlite3
import json
from typing import List
from src.constants import MOBMENTOR_DB_FILE_NAME, MOBMENTOR_DB_SCRIPT_PATH

class DatabaseHandler():
    def __init__(self) -> None:
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        data = self.__load_data_from_file('dictionary.json')
        self.fill_db(data)

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

    def __load_data_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def fill_db(self, data) -> None:
        for module in data:
            self.cursor.execute('''
                INSERT INTO Modules(
                    module_name, module_descr
                )
                VALUES (?, ?)
                ''',
                (module['module_name'], module['module_descr'])
            )
            module_id = self.cursor.lastrowid

            topic_id = 1
            for topic in module.get('topics', []):
                self.cursor.execute('''
                    INSERT INTO Topics(
                        module_id, topic_id, topic_name, topic_text
                    )
                    VALUES (?, ?, ?, ?)
                    ''',
                    (module_id, topic_id,
                     topic['topic_name'], topic['topic_text'])
                )

                question_id = 1
                for question in topic.get('topic_questions', []):
                    self.cursor.execute('''
                    INSERT INTO Questions(
                        module_id, topic_id, question_id, question_text, question_answer_text
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (module_id, topic_id, question_id,
                     question['question_text'],
                     question['question_answer_text']))
                topic_id += 1
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


    def get_questions(self, module_id: int, topic_id: int) -> List[sqlite3.Row]:
        self.cursor.execute('''
            SELECT *
            FROM Questions
            WHERE module_id = ? AND topic_id = ?
        ''', (module_id, topic_id,))
        return self.cursor.fetchall()


    def get_question_answer(self, module_id: int,
                            topic_id: int, question_id: int) -> sqlite3.Row:
        self.cursor.execute('''
            SELECT *
            FROM Questions
            WHERE module_id = ? AND topic_id = ? AND question_id = ?
        ''', (module_id, topic_id, question_id,))
        return self.cursor.fetchone()


database_handler = DatabaseHandler()
