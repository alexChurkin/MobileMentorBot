import sqlite3
import json
import os

conn = None
cursor = None


def db_connect():
    conn = sqlite3.connect('mobmentor.db')
    cursor = conn.cursor()


def db_disconnect():
    conn.close()


def create_tables():
    with open(os.path.join("src", "sql", "create_tables.sql"), 'r',
              encoding='utf-8') as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()


def load_data_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def fill_db(data):
    for module in data:
        cursor.execute('INSERT INTO Modules (module_name, module_descr) VALUES (?, ?)',
                       (module['module_name'], module['module_descr']))
        module_id = cursor.lastrowid

        for topic in module.get('topics', []):
            cursor.execute(
                'INSERT INTO Topics (module_id, topic_name, topic_text) VALUES (?, ?, ?)',
                           (module_id, topic['topic_name'], topic['topic_text']))
            topic_id = cursor.lastrowid

            for question in topic.get('topic_questions', []):
                cursor.execute(
                    'INSERT INTO Questions (topic_id, question_text, question_answer_text) VALUES (?, ?, ?)',
                    (topic_id, question['question_text'], question['question_answer_text']))
    conn.commit()


def get_topics_of_module(module_id):
    cursor.execute('''
    SELECT Topics.id, Topics.topic_name FROM Topics
    JOIN Modules ON Topics.module_id = Modules.id
    WHERE Modules.id = ?
    ''', (module_id,))
    return cursor.fetchall()


def get_topic_by_id(topic_id):
    cursor.execute('''
    SELECT topic_name, topic_text FROM Topics
    WHERE id = ?
    ''', (topic_id,))
    return cursor.fetchone()


if __name__ == "__main__":
    db_connect()

    create_tables()
    data = load_data_from_file('dictionary.json')
    fill_db(data)
    topics = get_topics_of_module(module_id=1)
    print("Topics for 1:", topics)

    topic = get_topic_by_id(1)
    print("Topic with ID 1:", topic)

    db_disconnect()
