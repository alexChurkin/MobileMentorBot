DROP TABLE IF EXISTS Modules;
DROP TABLE IF EXISTS Topics;
DROP TABLE IF EXISTS Questions;

CREATE TABLE IF NOT EXISTS Modules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name TEXT NOT NULL,
        module_descr TEXT
);

CREATE TABLE IF NOT EXISTS Topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id INTEGER,
        topic_name TEXT NOT NULL,
        topic_text TEXT,
        FOREIGN KEY(module_id) REFERENCES Modules(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        question_text TEXT NOT NULL,
        question_answer_text TEXT,
        FOREIGN KEY(topic_id) REFERENCES Topics(id) ON DELETE CASCADE
)
