DROP TABLE IF EXISTS Modules;
DROP TABLE IF EXISTS Topics;
DROP TABLE IF EXISTS Questions;
DROP VIEW IF EXISTS TopicsView;

CREATE TABLE Modules (
        module_id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name TEXT NOT NULL,
        module_descr TEXT
);

CREATE TABLE Topics (
        module_id INTEGER,
        topic_id INTEGER,
        topic_name TEXT NOT NULL,
        topic_text TEXT,
        PRIMARY KEY(module_id, topic_id),
        FOREIGN KEY(module_id) REFERENCES Modules(module_id) ON DELETE CASCADE
);

CREATE TABLE Questions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id INTEGER,
        topic_id INTEGER,
        question_text TEXT NOT NULL,
        question_answer_text TEXT,
        FOREIGN KEY(module_id) REFERENCES Modules(module_id) ON DELETE CASCADE
);

CREATE VIEW TopicsView AS
SELECT Modules.module_id AS module_id,
       Modules.module_name AS module_name,
       Topics.topic_id AS topic_id,
       Topics.topic_name AS topic_name,
       Topics.topic_text AS topic_text
FROM Topics
LEFT JOIN Modules ON
Topics.module_id = Modules.module_id;
