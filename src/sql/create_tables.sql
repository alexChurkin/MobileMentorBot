CREATE TABLE IF NOT EXISTS Modules (
        module_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        module_name  TEXT NOT NULL,
        module_descr TEXT
);

CREATE TABLE IF NOT EXISTS Topics (
        module_id  INTEGER NOT NULL,
        topic_id   INTEGER NOT NULL,
        topic_name TEXT NOT NULL,
        topic_text TEXT,
        PRIMARY KEY(module_id, topic_id),
        FOREIGN KEY(module_id) REFERENCES Modules(module_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Questions (
        question_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id            INTEGER NOT NULL,
        topic_id             INTEGER NOT NULL,
        user_name            TEXT,
        question_text        TEXT NOT NULL,
        question_answer_text TEXT,
        FOREIGN KEY(module_id, topic_id)   REFERENCES Topics(module_id, topic_id)   ON DELETE CASCADE,
        FOREIGN KEY(user_name)             REFERENCES Users(user_name)              ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Users (
        user_name TEXT NOT NULL,
        role_id   INTEGER NOT NULL,
        psswd     TEXT,
        FOREIGN KEY(role_id) REFERENCES UserRoles(role_id) ON DELETE RESTRICT,
        PRIMARY KEY(user_name, role_id)
);

CREATE TABLE IF NOT EXISTS UserRoles (
        role_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        role_meaning TEXT NOT NULL
);

CREATE VIEW IF NOT EXISTS TopicsView AS
SELECT Modules.module_id   AS module_id,
       Modules.module_name AS module_name,
       Topics.topic_id     AS topic_id,
       Topics.topic_name   AS topic_name,
       Topics.topic_text   AS topic_text
FROM Topics
LEFT JOIN Modules ON
Topics.module_id = Modules.module_id;
