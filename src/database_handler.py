import sqlite3
import json
from src.constants import MOBMENTOR_DB_FILE_NAME, MOBMENTOR_DB_SCRIPT_PATH

class DatabaseHandler():
    def __init__(self) -> None:
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        data = self.__load_data_from_file('dictionary.json')
        self.fill_db(data)

    def connect(self):
        self.conn = sqlite3.connect(MOBMENTOR_DB_FILE_NAME)
        self.cursor = self.conn.cursor()

    def disconnect(self):
        self.conn.close()

    def create_tables(self):
        with open(MOBMENTOR_DB_SCRIPT_PATH, 'r',
                encoding='utf-8') as f:
            sql_script = f.read()
        self.cursor.executescript(sql_script)
        self.conn.commit()

    def __load_data_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def fill_db(self, data):
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

            for topic in module.get('topics', []):
                self.cursor.execute('''
                    INSERT INTO Topics(
                        module_id, topic_name, topic_text
                    )
                    VALUES (?, ?, ?)
                    ''',
                    (module_id, topic['topic_name'], topic['topic_text'])
                )
                topic_id = self.cursor.lastrowid

                for question in topic.get('topic_questions', []):
                    self.cursor.execute('''
                    INSERT INTO Questions(
                        topic_id, question_text, question_answer_text
                    )
                    VALUES (?, ?, ?)
                    ''',
                    (topic_id, question['question_text'],
                     question['question_answer_text']))
        self.conn.commit()

    def get_modules_list(self):
        self.cursor.execute('''
            SELECT id, module_name
            FROM Modules
        ''')
        return self.cursor.fetchall()

    def get_module_name(self, module_id: int):
        self.cursor.execute('''
            SELECT module_name
            FROM Modules
            WHERE id = ?
        ''', (module_id,))
        return self.cursor.fetchone()

    def get_topics_list(self, module_id: int):
        self.cursor.execute('''
            SELECT Topics.id, Topics.topic_name
            FROM Topics
            JOIN Modules ON Topics.module_id = Modules.id
            WHERE Modules.id = ?
        ''', (module_id,))
        return self.cursor.fetchall()

    def get_topic_by_id(self, topic_id: int):
        self.cursor.execute('''
            SELECT topic_name, topic_text
            FROM Topics
            WHERE id = ?
        ''', (topic_id,))
        return self.cursor.fetchone()


database_handler = DatabaseHandler()
